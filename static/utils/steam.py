import sqlite3
from sys import exception

from bs4 import BeautifulSoup
import requests
import re
import json
import os


class SteamLibrary:
    def __init__(self):
        self.steam_path = self.get_steam_path()
        self.db = sqlite3.connect("static/glibrary.db")
        self.db.row_factory = sqlite3.Row

    def get_steam_path(self):
        with open("static/locations.json", 'r') as f:
            config = json.load(f)
            return config['steampath']

    def load_steam_api(self, steam_id):
        cursor = self.db.cursor()
        cursor.execute('SELECT accountid, steamAPI FROM accounts')
        rows = cursor.fetchall()
        steam_api = None
        for row in rows:
            if row['steamAPI']:
                steam_api = row['steamAPI']
            if row['steamAPI'] and row['accountid'] == steam_id:
                steam_api = row['steamAPI']
                return steam_api
        return steam_api if steam_api else None

    def get_last_played_from_disk(self, steam_id):
        converted_steam_id = int(steam_id) - 76561197960265728
        file_path = f'{self.steam_path}\\userdata\\{converted_steam_id}\\config\\localconfig.vdf'
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        app_pattern = re.compile(r'"(\d+)"\s*{(?:[^{}]*{[^{}]*})*\s*"LastPlayed"\s*"(\d+)"')
        matches = app_pattern.findall(content)
        tab = []
        for app_id, last_played in matches:
            tab.append({'gameid': int(app_id), 'lastplayed': last_played})
        return tab
#TODO: zajebac bardziej uniwersalny sposob zeby to dzialalo
    def without_api(self, steam_id):
        try:
            games = []
            session = requests.Session()
            steam_profile_url = f'https://steamcommunity.com/profiles/{steam_id}/games/?tab=all'
            cookies = {
                'steamLoginSecure': "76561199807088256%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MDAwRF8yNUQ2RUQ2NV80QzcwQyIsICJzdWIiOiAiNzY1NjExOTk4MDcwODgyNTYiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3Mzk4MTU1OTEsICJuYmYiOiAxNzMxMDg3OTQ4LCAiaWF0IjogMTczOTcyNzk0OCwgImp0aSI6ICIwMDA0XzI1RDZFRDY1XzU4NkMyIiwgIm9hdCI6IDE3Mzk3Mjc1MzksICJydF9leHAiOiAxNzU3NjQ4NTU5LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiODMuMzEuMTQuMTExIiwgImlwX2NvbmZpcm1lciI6ICI4My4zMS4xNC4xMTEiIH0.Tjc7Vi6_R_sXWk_IoVYz5g9jFdo1S6JBF2tefzlJ3tPl3b8M6hXsYBEq3lRFeegtF6aMlgxnBP-mqV1UlnizDA"}
            session.cookies.update(cookies)
            response = session.get(steam_profile_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data_json = soup.find('template', {'data-profile-gameslist': True})['data-profile-gameslist']
                data = json.loads(data_json.replace('&quot;', '"'))
                dupa = data.get('rgGames', [])
                return dupa
            return []
        except Exception as e:
            print("chujnia z grzybem")
            return []

    def get_steam_games(self, steam_id, steam_api):
        api = self.load_steam_api(steam_id)
        if not api:
            return self.without_api(steam_id)
        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': api,
            'steamid': steam_id,
            'include_appinfo': 'true',
            'include_played_free_games': 'true',
            'appids_filter': ''
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'games' in data['response']:
                games = data['response']['games']
            else:
                games = []
            return games
        else:
            return []

    def get_steam_name(self, steam_id):
        try:
            config_path = f'{self.steam_path}\\config\\loginusers.vdf'
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read()
            steam_id_str = str(steam_id)
            user_pattern = re.compile(r'"' + re.escape(steam_id_str) + r'"\s*{[^{}]*"AccountName"\s*"([^"]+)"')
            match = user_pattern.search(content)
            if match:
                return match.group(1)
            else:
                return "Konto"
        except:
            return "Konto"

    def update_steam_ids(self):
        cursor = self.db.cursor()
        try:
            config_path = f'{self.steam_path}\\config\\loginusers.vdf'
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read()
            pattern = r'"(\d+)"\s*\{\s*"AccountName"\s*"([^"]+)"'
            steam_ids = re.findall(pattern, content)
            for steam_id in steam_ids:
                cursor.execute('SELECT * FROM accounts WHERE accountid = ?', (steam_id[0],))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute('INSERT INTO accounts (accountName, platform, accountid) VALUES (?, ?, ?)',
                                  (steam_id[1], "Steam", steam_id[0]))
        except Exception as e:
            print(f"Error updating Steam IDs: {e}")
        self.db.commit()

    def close(self):
        self.db.close()

if __name__ == '__main__':
    steam_manager = SteamLibrary()
    steam_manager.update_steam_ids()
    steam_manager.close()