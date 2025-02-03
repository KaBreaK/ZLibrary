import requests
import json
from bs4 import BeautifulSoup

session = requests.Session()
steam_profile_url = f'https://steamcommunity.com/profiles/76561199105400234/games/?tab=all'
cookies = {
            'steamRefresh_steam': "76561199807088256%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInN0ZWFtIiwgInN1YiI6ICI3NjU2MTE5OTgwNzA4ODI1NiIsICJhdWQiOiBbICJ3ZWIiLCAicmVuZXciLCAiZGVyaXZlIiBdLCAiZXhwIjogMTc1NjIwMTk3OCwgIm5iZiI6IDE3Mjk3MjI4ODYsICJpYXQiOiAxNzM4MzYyODg2LCAianRpIjogIjAwMEZfMjVDMzBCODRfNzFCNDAiLCAib2F0IjogMTczODM2Mjg4NiwgInBlciI6IDEsICJpcF9zdWJqZWN0IjogIjc5LjE4NC4xOTQuOTIiLCAiaXBfY29uZmlybWVyIjogIjc5LjE4NC4xOTQuOTIiIH0.nLvfpoBkdlSbOnYO7DcFdQC0fWc4eeCOLj2ODc1ZWAvblMemMzGJPel4JJWpcRsuik4isZXkvRbOyS7jEUjKDA"
        }
session.cookies.update(cookies)
response = session.get(steam_profile_url)
if response.status_code == 200:
    data = {"redir": "https://steamcommunity.com/profiles/76561199105400234/games/?tab=all"}
    response = session.post("https://login.steampowered.com/jwt/ajaxrefresh", data=data)
    data = {"auth": response.json()['auth'],
            "nonce": response.json()['nonce'],
            "redir": response.json()['redir'],
            "steamID": response.json()['steamID']
            }
    response = session.post("https://steamcommunity.com/login/settoken", data=data)
    response = session.get(steam_profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_json = soup.find('template', {'data-profile-gameslist': True})['data-profile-gameslist']
    data = json.loads(data_json.replace('&quot;', '"'))
    dupa = data.get('rgGames', [])
    print(dupa)