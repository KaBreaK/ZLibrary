
import subprocess
import winreg
import vdf
import psutil
import json

class SteamRun:
    def __init__(self):
        self.steam_path = f"{self.get_steam_path()}/steam.exe"
        self.loginusers_path = f"{self.get_steam_path()}/config/loginusers.vdf"
        # self.steam_path = f"C:/Program Files (x86)/Steam/steam.exe"
        # self.loginusers_path = f"C:/Program Files (x86)/Steam/config/loginusers.vdf"
        self.registry_path = r"Software\Valve\Steam"
    def get_steam_path(self):
        with open("static/locations.json", 'r') as f:
            config = json.load(f)
            return config['steampath']
    def run(self, steamid, appid=None):
        self.kill_steam_process()
        self.steam_login_user(steamid)
        self.launch_steam(appid)
    def kill_steam_process(self):
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'].lower() == 'steam.exe':
                    process.terminate()
                    print("Steam został wyłączony.")
                    break
        except Exception as e:
            print(f"Błąd przy zamykaniu procesu Steama: {e}")

    def steam_login_user(self, steamid):
        try:
            with open(self.loginusers_path, 'r') as f:
                data = vdf.load(f)
            username = None
            print(steamid)
            for userid, user in data["users"].items():
                if userid == steamid:
                    user["AllowAutoLogin"] = 1
                    user["MostRecent"] = 1
                    username = user["AccountName"]
                else:
                    user["MostRecent"] = 0
            if username:
                self.add_registry_entries(username)
            with open(self.loginusers_path, 'w') as f:
                vdf.dump(data, f)
        except Exception as e:
            print(f"Błąd przy logowaniu użytkownika: {e}")

    def add_registry_entries(self, username):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, username)
                winreg.SetValueEx(key, "RememberPassword", 0, winreg.REG_DWORD, 1)
            print("Rejestry zostały dodane.")
        except Exception as e:
            print(f"Błąd przy dodawaniu rejestrów: {e}")

    def launch_steam(self, appid=None):
        try:
            if appid:
                command = [self.steam_path, f"steam://run/{appid}"]
            else:
                command = [self.steam_path]

            subprocess.Popen(command)
            print("Uruchamianie Steama...")
        except Exception as e:
            print(f"Błąd przy uruchamianiu Steama: {e}")

if __name__ == "__main__":
    manager = SteamRun()
    manager.run("76561199105400234", 730)
