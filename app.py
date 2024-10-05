from flask import Flask
import sqlite3
import sys
import os
from sites.index import index_bp

app = Flask(__name__)
app.secret_key = 'CHUJ'

# Otwórz połączenie z bazą danych
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

# Utwórz tabelę 'gamespec'
cursor.execute('''
CREATE TABLE IF NOT EXISTS `gamespec` (
    game_name TEXT PRIMARY KEY,
    fav BOOLEAN,
    completed BOOLEAN
);
''')

db.commit()
db.close()

app.register_blueprint(index_bp)

if __name__ == '__main__':
    app.run(debug=True)
