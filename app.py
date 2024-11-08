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
    "gameLibraries": {},
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
        `gamePhoto` TEXT NOT NULL,
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
        print(f"Plik {file_path} nie istnieje. Tworzę domyślny plik konfiguracyjny.")
        with open(file_path, 'w') as f:
            json.dump(default_config, f, indent=4)
app.register_blueprint(index_bp)
app.register_blueprint(settings_bp)
@app.route('/shutdown', methods=['POST'])
def shutdown():
    os._exit(0)
    return 'Server shutting down...'

if __name__ == '__main__':
    create_config()
    app.run(debug=True, port=8090)
