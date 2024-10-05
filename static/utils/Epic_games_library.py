import json
import os
import requests

CACHE_DIR = os.path.expanduser("")


class EpicGamesStoreService:
    token_path = os.path.join(CACHE_DIR, ".egs.token")
    login_url = (
        "https://www.epicgames.com/id/login?redirectUrl="
        "https%3A//www.epicgames.com/id/api/redirect%3F"
        "clientId%3D34a02cf8f4414e29b15921876da36f9a%26responseType%3Dcode"
    )
    redirect_uri = "https://www.epicgames.com/id/api/redirect"
    oauth_url = "https://account-public-service-prod03.ol.epicgames.com"
    catalog_url = "https://catalog-public-service-prod06.ol.epicgames.com"
    library_url = "https://library-service.live.use1a.on.epicgames.com"

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "EpicGamesLauncher/11.0.1-14907503+++Portal+Release-Live "
        "UnrealEngine/4.23.0-14907503+++Portal+Release-Live "
        "Chrome/84.0.4147.38 Safari/537.36"
    )

    def __init__(self):
        self.session = requests.session()
        self.session.headers["User-Agent"] = self.user_agent
        if os.path.exists(self.token_path):
            with open(self.token_path, encoding="utf-8") as token_file:
                try:
                    self.session_data = json.loads(token_file.read())
                except:
                    self.session_data = {}
        else:
            self.session_data = {}

    @property
    def http_basic_auth(self):
        return requests.auth.HTTPBasicAuth("34a02cf8f4414e29b15921876da36f9a", "daafbccc737745039dffe53d94fc76cf")

    def is_connected(self):
        return self.is_authenticated()

    def login_callback(self, content):
        print("Login to EGS successful")
        content_json = json.loads(content.decode())
        session_id = content_json["authorizationCode"]

        self.start_session(authorization_code=session_id)
        print("Service login complete")

    def resume_session(self):
        self.session.headers["Authorization"] = "bearer %s" % self.session_data["access_token"]
        response = self.session.get("%s/account/api/oauth/verify" % self.oauth_url)
        if response.status_code >= 500:
            response.raise_for_status()

        response_content = response.json()
        if "errorMessage" in response_content:
            raise RuntimeError(response_content)
        return response_content

    def start_session(self, exchange_code=None, authorization_code=None):
        if exchange_code:
            params = {"grant_type": "exchange_code", "exchange_code": exchange_code, "token_type": "eg1"}
        elif authorization_code:
            params = {"grant_type": "authorization_code", "code": authorization_code, "token_type": "eg1"}
        else:
            params = {
                "grant_type": "refresh_token",
                "refresh_token": self.session_data["refresh_token"],
                "token_type": "eg1",
            }

        response = self.session.post(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
            data=params,
            auth=self.http_basic_auth,
        )
        if response.status_code >= 500:
            response.raise_for_status()

        response_content = response.json()
        if "error" in response_content:
            raise RuntimeError(response_content)
        with open(self.token_path, "w", encoding="utf-8") as auth_file:
            auth_file.write(json.dumps(response_content, indent=2))
        self.session_data = response_content

    def get_game_playtime(self):
        self.resume_session()
        response = self.session.get("%s/library/api/public/playtime/account/%s/all" % (self.library_url, self.session_data["account_id"]))
        if response.status_code >= 500:
            response.raise_for_status()
        response_content = response.json()
        return response_content
    def get_game_details(self, asset):
        namespace = asset["namespace"]
        catalog_item_id = asset["catalogItemId"]
        response = self.session.get(
            "%s/catalog/api/shared/namespace/%s/bulk/items" % (self.catalog_url, namespace),
            params={
                "id": catalog_item_id,
                "includeDLCDetails": True,
                "includeMainGameDetails": True,
                "country": "US",
                "locale": "en",
            },
        )
        response.raise_for_status()

        asset.update(response.json()[catalog_item_id])
        return asset
    def get_game_library(self):
        self.resume_session()
        response = self.session.get(
            "%s/library/api/public/items" % self.library_url, params={"includeMetadata": "true"}
        )
        response.raise_for_status()
        resData = response.json()
        records = resData["records"]
        cursor = resData["responseMetadata"].get("nextCursor", None)
        while cursor:
            response = self.session.get(
                "%s/library/api/public/items" % self.library_url, params={"includeMetadata": "true", "cursor": cursor}
            )
            response.raise_for_status()
            resData = response.json()
            records.extend(resData["records"])
            cursor = resData["responseMetadata"].get("nextCursor", None)
        games = []
        for record in records:
            if record["namespace"] == "ue":
                continue
            game_details = self.get_game_details(record)
            games.append(game_details)
        return games

    def import_games(self):
        ggames = []
        library_data = self.get_game_library()
        #print(self.get_game_playtime())
        #print(games)
        #print(self.get_game_details(games[1]))
        #print(self.get_game_lastplayed())
        return library_data

    def authenticate(self):
        if not self.is_connected():
            raise RuntimeError("Not authenticated")
        print("User is authenticated")

    def is_authenticated(self):
        return bool(self.session_data.get("access_token"))

    def login(self, authcode):
        authorization_code = authcode
        self.start_session(authorization_code=authorization_code)

    def run(self, authcode):
        try:
            self.authenticate()
            games = []
            seen_sandbox_names = set()
            gameslibrary, gamesplayime = self.import_games(), self.get_game_playtime()

            artifact_to_playtime = {playtime['artifactId']: playtime['totalTime'] for playtime in gamesplayime}
            for game in gameslibrary:
                sandbox_name = game['sandboxName']

                # Sprawdzenie, czy sandboxName jest już w zestawie
                if sandbox_name not in seen_sandbox_names:
                    artifact_id = game['appName']
                    total_time = artifact_to_playtime.get(artifact_id, 0)

                    # Dodanie nowego sandboxName do zestawu
                    seen_sandbox_names.add(sandbox_name)

                    # Dodanie gry do listy gier
                    games.append({
                        'runUrl': f'{game["namespace"]}%3A{game["catalogItemId"]}%3A{game["appName"]}',
                        'sandboxName': game['sandboxName'],
                        'gameimage': next(
                            (image["url"] for image in game["keyImages"] if image["type"] == "DieselGameBoxTall"),
                            None),
                        'totalTime': total_time
                    })
            return games
        except RuntimeError:
            self.login(authcode)
            games = []
            seen_sandbox_names = set()
            gameslibrary, gamesplayime = self.import_games(), self.get_game_playtime()
            artifact_to_playtime = {playtime['artifactId']: playtime['totalTime'] for playtime in gamesplayime}
            for game in gameslibrary:
                sandbox_name = game['sandboxName']

                # Sprawdzenie, czy sandboxName jest już w zestawie
                if sandbox_name not in seen_sandbox_names:
                    artifact_id = game['appName']
                    total_time = artifact_to_playtime.get(artifact_id, 0)

                    # Dodanie nowego sandboxName do zestawu
                    seen_sandbox_names.add(sandbox_name)

                    # Dodanie gry do listy gier
                    games.append({
                        'runUrl': f'{game["namespace"]}%3A{game["catalogItemId"]}%3A{game["appName"]}',
                        'sandboxName': game['sandboxName'],
                        'gameimage': next(
                            (image["url"] for image in game["keyImages"] if image["type"] == "DieselGameBoxTall"),
                            None),
                        'totalTime': total_time
                    })
            return games


if __name__ == "__main__":
    service = EpicGamesStoreService()
    games = service.run('4a184f36a3ea4c99ae905b21e4b4a631')
    for game in games:
        print(game)