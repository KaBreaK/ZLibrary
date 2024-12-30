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
            games.append(record)
        return games

    def import_games(self):
        library_data = self.get_game_library()
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
    def get_images(self, ids):
        ns_item_ids = [f"{item['namespace']}:{item['catalogItemId']}" for item in ids]
        data = {
            'nsItemId': ns_item_ids
        }
        url = "https://catalog-public-service-prod06.ol.epicgames.com/catalog/api/shared/bulk/namespaces/items?includeDLCDetails=false&includeMainGameDetails=false&country=US&locale=en"
        response = self.session.post(url, data=data)
        return response.json()
    def run(self, authcode):
        try:
            self.authenticate()
        except:
            self.login(authcode)
        a = self.import_games()
        b = self.get_game_playtime()
        c = self.get_images(a)
        total_time_dict = {}
        for item in b:
            total_time_dict[item['artifactId']] = item['totalTime']
        result = []
        for key, value in c.items():
            if all(category['path'] != 'games' for category in value['categories']) or 'mainGameItem' in value:
                continue
            title = value['title']
            runUrl = f'{value["namespace"]}%3A{value["id"]}%3A{value['releaseInfo'][0]['appId']}'
            total_time = total_time_dict.get(value['releaseInfo'][0]['appId'], 0)
            diesel_game_box_tall = None
            for image in value['keyImages']:
                if image['type'] == 'DieselGameBoxTall':
                    diesel_game_box_tall = image['url']
                    break
            result.append(
                {'runUrl': runUrl, 'sandboxName': title, 'gameimage': diesel_game_box_tall, 'totalTime': total_time})
        return result


if __name__ == "__main__":
    service = EpicGamesStoreService()
    games = service.run('7cf4a20cbf7f44bf94728c3b85cb3468')