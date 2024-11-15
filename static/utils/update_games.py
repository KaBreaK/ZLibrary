import sqlite3
import requests
import os
import re
import json
from .Epic_games_library import EpicGamesStoreService
from .steam import get_steam_games, get_lastplayed_from_disc
#from steam import get_steam_games, get_lastplayed_from_disc

def update_games():
    steamaccs = []
    epicaccs = []
    db = sqlite3.connect("static/glibrary.db")
    #db = sqlite3.connect("../glibrary.db")
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
                cursor.execute("SELECT id FROM accounts WHERE accountid = ?", (steam[0],))
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
            print(games)
            for game in games:
                cursor.execute(
                    'INSERT INTO games (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?,?)',
                    (game['sandboxName'], game['runUrl'], game['gameimage'], game['totalTime']/60, 0, epic))
        except:
            pass
    db.commit()
    db.close()
    steamIgmaes()
    epicIgames()


def steamIgmaes():
    with open("static/settings.json", 'r') as f:
        config = json.load(f)
        libaryPaths = config['gameLibraries']
    print(libaryPaths)
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("UPDATE games SET installed  = 0 WHERE account_id IN (SELECT id FROM Accounts WHERE platform = 'Steam')")
    installedGames = []
    for path in libaryPaths:
        try:
            installedGames = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        except:
            pass
    for game in installedGames:
        cursor.execute("UPDATE games SET installed = 1 WHERE GameName = ?", (game,))
    db.commit()
    db.close()

def epicIgames():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("UPDATE games SET installed  = 0 WHERE account_id IN (SELECT id FROM Accounts WHERE platform = 'EPIC')")
    manifests_path = "C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
    if not os.path.exists(manifests_path):
        print("No valid path for EGS games manifests in %s", manifests_path)
        return
    for manifest in os.listdir(manifests_path):
        if not manifest.endswith(".item"):
            continue
        with open(os.path.join(manifests_path, manifest), encoding="utf-8") as manifest_file:
            manifest_content = json.loads(manifest_file.read())
        if manifest_content["MainGameAppName"] != manifest_content["AppName"]:
            continue
        cursor.execute("UPDATE games SET installed = 1 WHERE GameName = ?", (manifest_content["AppName"],))
    db.commit()
    db.close()
if __name__ == '__main__':
    update_games()
    steamIgmaes()




