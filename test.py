import requests


def without_api(steam_id):
    response = requests.get(f'https://zlibrary.glitch.me/dane?steamId={steam_id}')
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return []
def get_steam_games(steam_id, steam_api):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': steam_api,
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

print(without_api(76561198807374475))
print(get_steam_games(76561198807374475, "5D2C684722E3A769185AB7B84EA7A1EB"))