import sqlite3
import requests
import os
import re
from .Epic_games_library import EpicGamesStoreService
from .steam import get_steam_games, get_lastplayed_from_disc


def update_games():
    steamaccs = []
    epicaccs = []
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('DELETE FROM games')
    cursor.execute('SELECT id, accountid, platform, steamAPI FROM accounts')
    rows = cursor.fetchall()
    for row in rows:
        if row['platform'] == 'Steam':
            steamacc = row['accountid'], row['steamAPI']
            steamaccs.append(steamacc)
        elif row['platform'] == 'EPIC':
            epicacc = row['id']
            epicaccs.append(epicacc)
    for steam in steamaccs:
        games = get_steam_games(steam[0], steam[1])
        for game in games:
            if 'Test' not in game['name']:
                cursor.execute("SELECT id FROM accounts WHERE accountid = ?", (steam,))
                ids = cursor.fetchall()
                ids = [id[0] for id in ids]
                accid = ids[0]
                if 'rtime_last_played' in game:
                    cursor.execute('INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)', (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg', game['playtime_forever'], game['rtime_last_played'], accid))
                else:
                    try:
                        filestime = get_lastplayed_from_disc(steam)
                        ftime = next((item for item in filestime if item['gameid'] == game['appid']), None)
                        print(ftime)
                        cursor.execute('INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)', (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg', game['playtime_forever'], ftime['lastplayed'], accid))
                    except:
                        cursor.execute('INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)', (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg', game['playtime_forever'], None, accid))
    for epic in epicaccs:
        service = EpicGamesStoreService()
        try:
            games = service.run(epic)
            for game in games:
                cursor.execute(
                    'INSERT INTO games (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?,?)',
                    (game['sandboxName'], game['runUrl'], game['gameimage'], game['totalTime']/60, 0, epic))
        except:
            pass
    db.commit()
    db.close()


if __name__ == "__main__":
    steamaccs = []
    epicaccs = []
    db = sqlite3.connect("../glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('DELETE FROM games')
    cursor.execute('SELECT id, accountid, platform, steamAPI FROM accounts')
    rows = cursor.fetchall()
    print("abc")
    print(rows)
    for row in rows:
        if row['platform'] == 'Steam':
            steamacc = row['accountid'], row['steamAPI']
            steamaccs.append(steamacc)
        elif row['platform'] == 'EPIC':
            epicacc = row['id']
            epicaccs.append(epicacc)
    for steam in steamaccs:
        print("abc")





