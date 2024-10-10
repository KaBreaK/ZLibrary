import sqlite3
import requests
import os
import re

STEAM_API_KEY = '5D2C684722E3A769185AB7B84EA7A1EB'

def get_lastplayed_from_disc(steamid):
    convertedsteamid = int(steamid) - 76561197960265728
    file_path = f'C:\\Program Files (x86)\\Steam\\userdata\\{convertedsteamid}\\config\\localconfig.vdf'
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    app_pattern = re.compile(r'"(\d+)"\s*{(?:[^{}]*{[^{}]*})*\s*"LastPlayed"\s*"(\d+)"')
    matches = app_pattern.findall(content)
    tab = []
    for app_id, last_played in matches:
        tab.append({'gameid': int(app_id), 'lastplayed': last_played})
    return tab

def get_steam_games(steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        'key': STEAM_API_KEY,
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
    try:
        config_path = 'C:\\Program Files (x86)\\Steam\\config\\loginusers.vdf'
        with open(config_path, 'r', encoding='utf-8') as file:
            content = file.read()
        steamid_str = str(steamid)
        user_pattern = re.compile(r'"' + re.escape(steamid_str) + r'"\s*{[^{}]*"AccountName"\s*"([^"]+)"')
        match = user_pattern.search(content)
        if match:
            return match.group(1)
        else:
            return None
    except:
        return "Konto"