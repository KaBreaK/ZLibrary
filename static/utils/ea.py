import requests
import re
import json
from urllib.parse import parse_qs, urlparse
class EAAuthenticator:
    def __init__(self, cookies_file="cookies.json", login=None, password=None):
        self.login = login
        self.password = password
        self.cookies_file = cookies_file
        self.session = requests.Session()
        self.headers = {
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Origin/10.6.0.00000 EAApp/13.363.3.5877 Chrome/109.0.5414.120 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9'
        }
        self.session.headers.update(self.headers)
        self.load_cookies()
    def extract_query_param(self, url, key):
        return parse_qs(urlparse(url).query).get(key, [None])[0]
    def load_cookies(self):
        try:
            with open(self.cookies_file, "r") as f:
                try:
                    cookies_dict = json.load(f)
                except:
                    cookies_dict = {}
                self.session.cookies.update(cookies_dict)
        except FileNotFoundError:
            pass

    def save_cookies(self):
        cookies_dict = self.session.cookies.get_dict()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies_dict, f, indent=4)

    def get_token(self):
        response0 = self.session.get(
            "https://accounts.ea.com/connect/auth?code_challenge_method=S256&sbiod_enabled=true&client_id=JUNO_PC_CLIENT&code_challenge=-eJ46pPQkRVov9wGI0rGm87peGtIlzWSXTvLsQDlTMg&redirect_uri=qrc:///html/login_successful.html&display=junoClient/login&locale=pl_PL&pc_sign=eyJhdiI6InYxIiwiYnNuIjoiRGVmYXVsdCBzdHJpbmciLCJnaWQiOjg1ODAsImhzbiI6IjJKMTgyMDAxMjc4NSIsIm1hYyI6IiQ3NDU2M2NiZTgxM2UiLCJtaWQiOiIxNDM1NDMxNDQxMDMzMjQxNjA1MyIsIm1zbiI6IkRlZmF1bHQgc3RyaW5nIiwic3YiOiJ2MiIsInRzIjoiMjAyNC0xMi0yNyAyMToyMToxNDo5NjAifQ.51hv-uBAjlVLIYtqpb7OtwgM9ruupKuzmvg8PQ6PjT8&nonce=1425492732&response_type=code",
            allow_redirects=False
        )
        location = response0.headers.get('Location')
        self.fid_value = self.extract_query_param(location, 'fid')
        if location and 'fid' in location:
            # execution1 = self.start_session(self.fid_value)
            # if execution1:
            #     print("rozpoczecie sesji udanie z execution1 =", execution1)
            # else:
            #     print("błąd rozpoczynania sesji")
            # execution2 = self.submit_login(execution1)
            # if execution2:
            #     print("logowanie mailem udanie z execution2 =", execution2)
            # else:
            #     print("błąd logowania mailem")
            # self.submit_password(execution2)
            # self.code = self.get_code()
            # if self.code:
            #     print("udalo sie uzyskac kod = ", self.code)
            # else:
            #     print("błąd pobierania kodu")



            execution1 = self.start_session(self.fid_value)
            execution2 = self.submit_login(execution1)
            self.submit_password(execution2)
            self.code = self.get_code()

            return self.extract_token()
        else:
            self.code = self.extract_query_param(location, 'code')
            return self.extract_token()

    def start_session(self, fid_value):
        response1 = self.session.post(f'https://signin.ea.com/p/juno/login?fid={fid_value}', allow_redirects=False)
        location = response1.headers.get('location')
        return self.extract_query_param(location, 'execution')

    def submit_login(self, execution1):
        logdata = {
            "email": self.login,
            "regionCode": "PL",
            "_eventId": "submit",
            "cid": "",
            "showAgeUp": "true",
            "loginMethod": "emailPassword",
            "_rememberMe": "on",
            "rememberMe": "on",
            "_loginInvisible": "on"
        }
        response2 = self.session.post(f'https://signin.ea.com/p/juno/login?execution={execution1}', data=logdata, allow_redirects=False)
        location = response2.headers.get('location')
        return self.extract_query_param(location, 'execution')
    def submit_password(self, execution2):
        if execution2:
            passdata = {
                "password": self.password,
                "_eventId": "submit",
                "cid": "",
                "showAgeUp": "true",
                "thirdPartyCaptchaResponse": "",
                "loginMethod": "emailPassword"
            }
            self.session.post(f'https://signin.ea.com/p/juno/login?execution={execution2}', data=passdata, allow_redirects=False)
        return None
    def get_code(self):
        response4 = self.session.get(f'https://accounts.ea.com/connect/auth?initref_replay=false&display=junoClient%2Flogin&response_type=code&code_challenge_method=S256&redirect_uri=qrc%3A%2F%2F%2Fhtml%2Flogin_successful.html&sbiod_enabled=true&locale=pl_PL&nonce=1425492732&client_id=JUNO_PC_CLIENT&code_challenge=-eJ46pPQkRVov9wGI0rGm87peGtIlzWSXTvLsQDlTMg&fid={self.fid_value}', allow_redirects=False)
        location = response4.headers.get('location')
        return self.extract_query_param(location, 'code')

    def extract_token(self):
        tokendata = {
            "token_format": "",
            "grant_type": "authorization_code",
            "client_id": "JUNO_PC_CLIENT",
            "client_secret": "4mRLtYMb6vq9qglomWEaT4ChxsXWcyqbQpuBNfMPOYOiDmYYQmjuaBsF2Zp0RyVeWkfqhE9TuGgAw7te",
            "redirect_uri": "qrc:///html/login_successful.html",
            "code": self.code,
            "code_verifier": "Zqmo2ZYUPSSvs13pG_xvqMi_oPKkJSyy-dIWCh41jrE"
        }
        response = self.session.post('https://accounts.ea.com/connect/token', data=tokendata, allow_redirects=False)
        self.save_cookies()
        return response.json().get('access_token')
    def get_game_stats(self, game_slug):
        headers = {"Authorization": "Bearer %s" % (self.token)}
        response = self.session.get(f'https://service-aggregation-layer.juno.ea.com/graphql?operationName=GetGamePlayTimes&variables=%7B%22gameSlugs%22%3A%5B%22{game_slug}%22%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%223f09b35e06b75c74d8ec3e520a598ebb5e2992b1e1268b6dd3b8ed99b9fafb29%22%7D%7D', headers=headers)
        try:
            game_data = response.json()["data"]["me"]["recentGames"]["items"][0]
        except:
            game_data = {'totalPlayTimeSeconds': 0, 'lastSessionEndDate': None}
        return {
            "playtime": game_data["totalPlayTimeSeconds"],
            "lastPlayed": game_data["lastSessionEndDate"]
        }
    def get_game_photo(self, game_slug):
        headers = {"Authorization": "Bearer %s" % (self.token)}
        response = self.session.get(f'https://service-aggregation-layer.juno.ea.com/graphql?operationName=GameImages&variables=%7B%22gameSlug%22%3A%22{game_slug}%22%2C%22locale%22%3A%22pl%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22eed06a15fc5865d120cd9f9197853f895610d82d1f0e1f412498afa73757c9df%22%7D%7D')
        return response.json()['data']['game']['packArt']['aspect9x16Image']['path']
    def get_library(self):
        result = []
        headers = {"Authorization": "Bearer %s" % (self.token)}
        response = self.session.get(
            'https://service-aggregation-layer.juno.ea.com/graphql?operationName=getPreloadedOwnedGames&variables=%7B%22isMac%22%3Afalse%2C%22isFreeToTryEnabled%22%3Atrue%2C%22locale%22%3A%22pl%22%2C%22limit%22%3A100%2C%22next%22%3A%220%22%2C%22type%22%3A%5B%22DIGITAL_FULL_GAME%22%2C%22PACKAGED_FULL_GAME%22%2C%22DIGITAL_EXTRA_CONTENT%22%2C%22PACKAGED_EXTRA_CONTENT%22%5D%2C%22entitlementEnabled%22%3Afalse%2C%22storefronts%22%3A%5B%22EA%22%2C%22STEAM%22%2C%22EPIC%22%5D%2C%22ownershipMethods%22%3A%5B%22UNKNOWN%22%2C%22ASSOCIATION%22%2C%22PURCHASE%22%2C%22REDEMPTION%22%2C%22GIFT_RECEIPT%22%2C%22ENTITLEMENT_GRANT%22%2C%22DIRECT_ENTITLEMENT%22%2C%22PRE_ORDER_PURCHASE%22%2C%22VAULT%22%2C%22XGP_VAULT%22%2C%22STEAM%22%2C%22STEAM_VAULT%22%2C%22STEAM_SUBSCRIPTION%22%2C%22EPIC%22%2C%22EPIC_VAULT%22%2C%22EPIC_SUBSCRIPTION%22%5D%2C%22platforms%22%3A%5B%22PC%22%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22b81758959a7470950683fba01ad7fc54c95ab195d4693c2485db93330da5314e%22%7D%7D',            headers=headers)
        items = response.json()["data"]["me"]["ownedGameProducts"]["items"]
        for item in items:
            result.append({
                "name": item["product"]["name"],
                "gameSlug": item["product"]["gameSlug"]
            })
        response = self.session.get(
            'https://service-aggregation-layer.juno.ea.com/graphql?operationName=getPreloadedOwnedGames&variables=%7B%22isMac%22%3Afalse%2C%22isFreeToTryEnabled%22%3Atrue%2C%22locale%22%3A%22pl%22%2C%22limit%22%3A100%2C%22next%22%3A%220%22%2C%22type%22%3A%5B%22DIGITAL_FULL_GAME%22%2C%22PACKAGED_FULL_GAME%22%2C%22DIGITAL_EXTRA_CONTENT%22%2C%22PACKAGED_EXTRA_CONTENT%22%5D%2C%22entitlementEnabled%22%3Atrue%2C%22storefronts%22%3A%5B%22EA%22%2C%22STEAM%22%2C%22EPIC%22%5D%2C%22ownershipMethods%22%3A%5B%22UNKNOWN%22%2C%22ASSOCIATION%22%2C%22PURCHASE%22%2C%22REDEMPTION%22%2C%22GIFT_RECEIPT%22%2C%22ENTITLEMENT_GRANT%22%2C%22DIRECT_ENTITLEMENT%22%2C%22PRE_ORDER_PURCHASE%22%2C%22VAULT%22%2C%22XGP_VAULT%22%2C%22STEAM%22%2C%22STEAM_VAULT%22%2C%22STEAM_SUBSCRIPTION%22%2C%22EPIC%22%2C%22EPIC_VAULT%22%2C%22EPIC_SUBSCRIPTION%22%5D%2C%22platforms%22%3A%5B%22PC%22%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22b81758959a7470950683fba01ad7fc54c95ab195d4693c2485db93330da5314e%22%7D%7D', headers=headers)
        items = response.json()["data"]["me"]["ownedGameProducts"]["items"]
        for item in items:
            if item["product"]["baseItem"]["gameType"] == "BASE_GAME":
                game_slug = item["product"]["gameSlug"]
                if not any(game["gameSlug"] == game_slug for game in result):
                    result.append({
                        "name": item["product"]["name"],
                        "gameSlug": game_slug
                    })
        return result
    def get_games(self):
        self.token = self.get_token()
        games = []
        list_games = self.get_library()
        for game in list_games:
            elobenc = self.get_game_stats(game["gameSlug"])
            elobenc_dict = {
                "GameName": game['name'],
                "gamePhoto": self.get_game_photo(game['gameSlug']),
                "playtime": elobenc['playtime'],
                "lastPlayed": elobenc['lastPlayed']
            }
            games.append(elobenc_dict)
        return games
if __name__ == "__main__":
    login = "makasko24@gmail.com"
    password = "Kalosze09"
    authenticator = EAAuthenticator(login, password)
    token = authenticator.get_games()
    for game in token:
        print(game)
