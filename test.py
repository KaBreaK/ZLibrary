import json
import os
import subprocess
from getpass import getpass
from pathlib import Path
from cryptography.fernet import Fernet

# Konfiguracja
CONFIG_DIR = Path.home() / ".steam_switcher"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"
KEY_FILE = CONFIG_DIR / "key.key"


# Szyfrowanie
def get_fernet():
    CONFIG_DIR.mkdir(exist_ok=True, parents=True)

    if not KEY_FILE.exists():
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        return Fernet(key)

    return Fernet(KEY_FILE.read_bytes())


fernet = get_fernet()


# Zarządzanie kontami
def load_accounts():
    if not ACCOUNTS_FILE.exists():
        return {}

    accounts = json.loads(ACCOUNTS_FILE.read_text())
    return {acc["name"]: {
        "username": acc["username"],
        "password": fernet.decrypt(acc["password"].encode()).decode()
    } for acc in accounts}


def save_account(name, username, password):
    accounts = load_accounts()
    accounts[name] = {
        "username": username,
        "password": fernet.encrypt(password.encode()).decode()
    }
    ACCOUNTS_FILE.write_text(json.dumps([
        {"name": name, **data} for name, data in accounts.items()
    ], indent=2))


# Steam
def find_steam():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0]) / "steam.exe"
        if steam_path.exists():
            return str(steam_path)
    except Exception:
        pass

    for path in [
        r"C:\Program Files (x86)\Steam\steam.exe",
        r"C:\Program Files\Steam\steam.exe"
    ]:
        if os.path.exists(path):
            return path

    return None


def launch_account(account_name):
    accounts = load_accounts()

    if account_name not in accounts:
        print(f"Nie znaleziono konta: {account_name}")
        return

    acc = accounts[account_name]
    steam_path = find_steam() or input("Podaj ścieżkę do steam.exe: ")

    subprocess.Popen(
        f'"{steam_path}" -login {acc["username"]} {acc["password"]}',
        shell=True
    )
    print(f"Uruchomiono Steam na koncie: {account_name}")


# Interfejs
def main_menu():
    while True:
        print("\n=== Steam Account Switcher ===")
        print("1. Dodaj nowe konto")
        print("2. Uruchom konto")
        print("3. Lista kont")
        print("4. Wyjdź")

        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            name = input("Nazwa konta: ").strip()
            username = input("Login Steam: ").strip()
            password = getpass("Hasło: ").strip()
            save_account(name, username, password)
            print("Konto dodane!")

        elif choice == "2":
            account_name = input("Podaj nazwę konta: ").strip()
            launch_account(account_name)

        elif choice == "3":
            accounts = load_accounts()
            print("\nZapisane konta:")
            for name, data in accounts.items():
                print(f"- {name} ({data['username']})")

        elif choice == "4":
            break

        else:
            print("Nieprawidłowy wybór!")


if __name__ == "__main__":
    main_menu()