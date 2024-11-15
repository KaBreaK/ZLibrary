import sqlite3
from dbm import error

import requests
import os
import re
import json
def getsteampath():
    with open("static/settings.json", 'r') as f:
        config = json.load(f)
        return config['steamPath']

STEAM_API_KEY = '5D2C684722E3A769185AB7B84EA7A1EB'
def loadSteamAPI():
    db = sqlite3.connect("static/glibrary.db")
    #db = sqlite3.connect("../glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute('SELECT steamAPI FROM accounts')
    rows = cursor.fetchall()
    for row in rows:
        if row['steamAPI']:
            STEAM_API_KEY = row['steamAPI']
    db.close()




def get_lastplayed_from_disc(steamid):
    convertedsteamid = int(steamid) - 76561197960265728
    steampath = getsteampath()
    file_path = f'{steampath}\\userdata\\{convertedsteamid}\\config\\localconfig.vdf'
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    app_pattern = re.compile(r'"(\d+)"\s*{(?:[^{}]*{[^{}]*})*\s*"LastPlayed"\s*"(\d+)"')
    matches = app_pattern.findall(content)
    tab = []
    for app_id, last_played in matches:
        tab.append({'gameid': int(app_id), 'lastplayed': last_played})
    return tab

def get_steam_games(steam_id, steamapi):
    loadSteamAPI()
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': (steamapi if steamapi else STEAM_API_KEY),
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
def get_steam_name(steamid):
    print("123")
    try:
        steampath = getsteampath()
        config_path = f'{steampath}\\config\\loginusers.vdf'
        #config_path = "C:\\Program Files (x86)\\Steam\\config\\loginusers.vdf"
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        steamid_str = str(steamid)
        user_pattern = re.compile(r'"' + re.escape(steamid_str) + r'"\s*{[^{}]*"AccountName"\s*"([^"]+)"')
        match = user_pattern.search(content)
        print("abc")
        if match:
            return match.group(1)
        else:
                return "Konto"
    except:
        return "Konto"

def get_steam_ids():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        steampath = getsteampath()
        #config_path = "C:\\Program Files (x86)\\Steam\\config\\config.vdf"
        config_path = f'{steampath}\\config\\config.vdf'
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        pattern = r'"SteamID"\s+"(\d+)"'
        steam_ids = re.findall(pattern, content)
        for steam_id in steam_ids:
            cursor.execute('SELECT 1 FROM accounts WHERE accountid = ?', (steam_id,))
            exists = cursor.fetchone()
            if  not exists:
                cursor.execute('INSERT INTO accounts (accountName, platform, accountid) VALUES (?, ?, ?)', (get_steam_name(steam_id), "Steam", steam_id))
    except error:
        return None
    db.commit()
    db.close()
if __name__ == '__main__':
    print(get_steam_ids())