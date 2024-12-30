from idlelib.outwin import file_line_pats
import json
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from sites.index import index_bp
from sites.settings import settings_bp

app = Flask(__name__, static_folder='dist', template_folder='dist')
app.secret_key = 'CHUJ'
CORS(app)

default_config = {
    "steamPath": "C:\\Program Files (x86)\\Steam\\",
    "gameLibraries": [],
    "theme": "dark"
}

def init_db():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `Accounts` (
        `id` INTEGER NOT NULL,
        `accountName` TEXT NOT NULL,
        `platform` TEXT NOT NULL,
        `steamAPI` TEXT,
        `accountid` TEXT,
        PRIMARY KEY (`id`)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `Games`(
        `GameName` TEXT NOT NULL,
        `epicRunUrl` TEXT,
        `steamid` INTEGER,
        `gamePhoto` TEXT,
        `playTime` INTEGER,
        `lastPlayed` INTEGER,
        `installed` BOOLEAN,
        `account_id` INTEGER NOT NULL,
        FOREIGN KEY (`account_id`) REFERENCES `Accounts` (`id`)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `gamespec` (
        game_name TEXT PRIMARY KEY,
        fav BOOLEAN,
        completed BOOLEAN
    );
    ''')

    db.commit()
    db.close()

init_db()
def create_config():
    file_path = "static/settings.json"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump(default_config, f, indent=4)
    update_game_libraries()


def update_game_libraries():
    file_path = "static/settings.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            config = json.load(f)

        steam_path = config.get("steamPath", "")
        if not steam_path:
            print("Brak ścieżki Steam w pliku konfiguracyjnym.")
            return

        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")

        if os.path.exists(vdf_path):
            with open(vdf_path, 'r') as vdf_file:
                vdf_content = vdf_file.read()

            library_paths = []
            start_idx = vdf_content.find('"path"')
            while start_idx != -1:
                start_idx = vdf_content.find('"path"', start_idx)
                if start_idx == -1:
                    break
                start_idx = vdf_content.find('"', start_idx + 7)
                if start_idx == -1:
                    print(f"Brak cudzysłowu na końcu path w pliku: {vdf_path}")
                    break
                end_idx = vdf_content.find('"', start_idx + 1)
                if end_idx == -1:
                    print(f"Nie znaleziono końca ścieżki dla path w pliku: {vdf_path}")
                    break
                path = vdf_content[start_idx + 1:end_idx]
                library_paths.append(path)
                start_idx = end_idx

            for path in library_paths:
                new_path = os.path.join(path, "steamapps", "common")
                new_path = os.path.normpath(new_path)  # Normalize the path to prevent extra backslashes
                if new_path not in config["gameLibraries"]:
                    config["gameLibraries"].append(new_path)

            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)

            print("dziala")
        else:
            print(f"Nie znaleziono pliku {vdf_path}.")
    else:
        print(f"Plik konfiguracyjny {file_path} nie istnieje.")
app.register_blueprint(index_bp)
app.register_blueprint(settings_bp)
@app.route('/shutdown', methods=['POST'])
def shutdown():
    os._exit(0)
    return 'Server shutting down...'

if __name__ == '__main__':
    create_config()
    app.run(debug=True, port=8090)
