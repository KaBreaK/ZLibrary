import sqlite3
import os
import json
from static.utils.Epic_games_library import EpicGamesStoreService
from static.utils.ea import EAAuthenticator
from static.utils.steam import SteamLibrary
import re
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
        self.steamService = SteamLibrary()
    def update_games(self, accounts):
        for account_id, api_key in accounts:
            games = self.steamService.get_steam_games(account_id, api_key)
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
                filestime = self.steamService.get_last_played_from_disk(acc_id, game['appid'])
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
        with open("static/locations.json", 'r') as f:
            config = json.load(f)
            steampath = config['steampath']
            manifestpath = os.path.join(steampath, "config", "libraryfolders.vdf")
        self.db.execute("UPDATE games SET installed  = 0 WHERE account_id IN (SELECT id FROM Accounts WHERE platform = 'Steam')")
        app_ids = set()
        with open(manifestpath, 'r', encoding='UTF-8') as file:
            f = file.read()
        pattern = r'"apps"\s*{\s*([^}]*)\s*}'
        matches = re.findall(pattern, f)
        for match in matches:
            ids = re.findall(r'"(\d+)"', match)
            app_ids.update(ids)
        for game in app_ids:
            self.db.execute("UPDATE games SET installed = 1 WHERE steamid = ?", (game,))



class EpicManager:
    def __init__(self, database):
        self.db = database

    def update_games(self, account_ids):

        for acc_id in account_ids:
            service = EpicGamesStoreService(acc_id)
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
        with open("static/locations.json", 'r') as f:
            config = json.load(f)
            steampath = config['epicpath']
            manifestpath = os.path.join(steampath, "Data", "Manifests")
        if not os.path.exists(manifestpath):
            print("No valid path for EGS games manifests in %s", manifestpath)
            return

        for manifest in os.listdir(manifestpath):
            if not manifest.endswith(".item"):
                continue
            with open(os.path.join(manifestpath, manifest), encoding="utf-8") as manifest_file:
                manifest_content = json.loads(manifest_file.read())
            if manifest_content["MainGameAppName"] != manifest_content["AppName"]:
                continue
            self.db.execute(
                "UPDATE games SET installed = 1 WHERE GameName = ?",
                (manifest_content["DisplayName"],)
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

