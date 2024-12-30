import sqlite3
import requests
import os
import json
#from .Epic_games_library import EpicGamesStoreService
#from .steam import get_steam_games, get_lastplayed_from_disc
from static.utils.Epic_games_library import EpicGamesStoreService
from static.utils.ea import EAAuthenticator
from static.utils.steam import get_steam_games, get_lastplayed_from_disc


class DatabaseManager:
    def __init__(self, db_path="static/glibrary.db"):
        self.db_path = db_path

    def connect(self):
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        return self.db

    def execute(self, query, params=()):
        cursor = self.db.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()


class SteamManager:
    def __init__(self, database):
        self.db = database

    def update_games(self, accounts):
        for account_id, api_key in accounts:
            games = get_steam_games(account_id, api_key)
            for game in games:
                if 'Test' in game['name']:
                    continue
                acc_id = self.get_account_id(account_id)
                self.insert_game(game, acc_id)

    def get_account_id(self, accountid):
        cursor = self.db.execute("SELECT id FROM accounts WHERE accountid = ?", (accountid,))
        ids = cursor.fetchall()
        return ids[0][0] if ids else None

    def insert_game(self, game, acc_id):
        if 'rtime_last_played' in game:
            self.db.execute(
                "INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)",
                (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg',
                 game['playtime_forever'], game['rtime_last_played'], acc_id)
            )
        else:
            try:
                filestime = get_lastplayed_from_disc((acc_id, game['appid']))
                last_played = next((item for item in filestime if item['gameid'] == game['appid']), None)
                self.db.execute(
                    "INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)",
                    (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg',
                     game['playtime_forever'], last_played['lastplayed'], acc_id)
                )
            except:
                self.db.execute(
                    "INSERT INTO games (gameName, steamid, gamePhoto, playTime, lastPlayed, account_id) VALUES  (?,?,?,?,?,?)",
                    (game['name'], game['appid'], f'https://cdn.akamai.steamstatic.com/steam/apps/{game["appid"]}/library_600x900.jpg',
                     game['playtime_forever'], None, acc_id)
                )

    def update_installed_games(self):
        with open("static/settings.json", 'r') as f:
            config = json.load(f)
            libaryPaths = config['gameLibraries']
        self.db.execute("UPDATE games SET installed  = 0 WHERE account_id IN (SELECT id FROM Accounts WHERE platform = 'Steam')")

        installedGames = []
        for path in libaryPaths:
            try:
                installedGames = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
            except Exception as r:
                print(r)
        for game in installedGames:
            self.db.execute("UPDATE games SET installed = 1 WHERE GameName = ?", (game,))



class EpicManager:
    def __init__(self, database):
        self.db = database

    def update_games(self, account_ids):
        service = EpicGamesStoreService()
        for acc_id in account_ids:
            try:
                games = service.run(acc_id)
                for game in games:
                    self.db.execute(
                        "INSERT INTO games (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?,?)",
                        (game['sandboxName'], game['runUrl'], game['gameimage'], game['totalTime'] / 60, 0, acc_id)
                    )
            except Exception as r:
                print(r)


    def update_installed_games(self):
        manifests_path = "C:\\ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests"
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
            self.db.execute(
                "UPDATE games SET installed = 1 WHERE GameName = ?",
                (manifest_content["AppName"],)
            )

class EAManager:
    def __init__(self, database):
        self.db = database

    def update_games(self, account_ids):

        for acc_id in account_ids:
            service = EAAuthenticator(f'{acc_id}.ea.token')
            try:
                games = service.get_games()
                for game in games:
                    self.db.execute(
                        "INSERT INTO games (gameName, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?)",
                        (game['GameName'], game['gamePhoto'], game['playtime'], game['lastPlayed'], acc_id)
                    )
            except Exception as r:
                print(r)

class GameManager:
    def __init__(self, db_path="static/glibrary.db"):
        self.db_manager = DatabaseManager(db_path)

    def update_games(self):
        db = self.db_manager.connect()
        db.execute('DELETE FROM games')
        accounts = db.execute('SELECT id, accountName, accountid, platform, steamAPI FROM accounts').fetchall()

        steam_accounts = [(row['accountid'], row['steamAPI']) for row in accounts if row['platform'] == 'Steam']
        epic_accounts = [row['id'] for row in accounts if row['platform'] == 'EPIC']
        ea_accounts = [row['id'] for row in accounts if row['platform'] == 'EA']

        steam_manager = SteamManager(self.db_manager)
        epic_manager = EpicManager(self.db_manager)
        ea_manager = EAManager(self.db_manager)

        steam_manager.update_games(steam_accounts)
        epic_manager.update_games(epic_accounts)
        ea_manager.update_games(ea_accounts)

        self.db_manager.commit()
        self.db_manager.close()

    def update_installed_games(self):
        self.db_manager.connect()
        steam_manager = SteamManager(self.db_manager)
        epic_manager = EpicManager(self.db_manager)

        steam_manager.update_installed_games()
        epic_manager.update_installed_games()

        self.db_manager.commit()
        self.db_manager.close()

def update_games():
    manager = GameManager()
    manager.update_games()
    manager.update_installed_games()
if __name__ == '__main__':
    manager = GameManager("static/glibrary.db")
    manager.update_games()
    manager.update_installed_games()
