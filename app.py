from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from sites.index import index_bp

app = Flask(__name__, static_folder='dist', template_folder='dist')
app.secret_key = 'CHUJ'
CORS(app)
# Otwórz połączenie z bazą danych
def init_db():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `User` (
        `Name` TEXT NOT NULL,
        `steampath` TEXT NOT NULL,
        `steamgamepath` TEXT NOT NULL,
        `ustawienie` TEXT NOT NULL,
        PRIMARY KEY (`Name`)
    );
    ''')

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

app.register_blueprint(index_bp)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/shutdown', methods=['POST'])
def shutdown():
    os._exit(0)
    return 'Server shutting down...'
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

if __name__ == '__main__':
    app.run(debug=True, port=8090)
