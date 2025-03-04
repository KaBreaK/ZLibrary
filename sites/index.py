from fastapi import APIRouter, HTTPException, Request
import sqlite3
from collections import defaultdict
from static.utils.update_games import update_games
from static.utils.start_game import SteamRun
import json

index_router = APIRouter()

def get_db_connection():
    print("Opening database connection")
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    return db

def get_accounts():
    print("Fetching accounts from database")
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM accounts")
        accounts = [dict(row) for row in cursor.fetchall()]
    print(f"Retrieved {len(accounts)} accounts")
    return accounts

def get_games(only_installed):
    print(f"Fetching games with only_installed={only_installed}")
    query = """
        SELECT games.*, accounts.id AS acc_id, accounts.accountName, accounts.platform, accounts.steamAPI, accounts.accountid,
               gamespec.fav, gamespec.completed
        FROM games
        LEFT JOIN accounts ON games.account_id = accounts.id
        LEFT JOIN gamespec ON games.GameName = gamespec.game_name
    """
    params = []
    if only_installed:
        query += " WHERE games.installed = ?"
        params.append(1)

    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    print(f"Retrieved {len(rows)} games from database")
    games_dict = defaultdict(lambda: {
        'totalPlayTime': 0,
        'playTimePerAccount': [],
        'maxPlayTime': 0
    })
    accounts = {}

    for row in rows:
        game_name = row['GameName']
        play_time = row['playTime']
        account_id = row['acc_id']

        games_dict[game_name].update({
            'name': game_name,
            'epicRunUrl': row['epicRunUrl'],
            'steamid': row['steamid'],
            'gamephoto': row['gamePhoto'],
            'lastPlayed': row['lastPlayed'],
            'installed': row['installed'] or 0,
            'fav': row['fav'] or 0,
            'completed': row['completed'] or 0,
        })

        games_dict[game_name]['totalPlayTime'] += play_time
        games_dict[game_name]['playTimePerAccount'].append({
            'accountName': row['accountName'],
            'platform': row['platform'],
            'playTime': play_time,
            'accountId': row['accountid']
        })

        if play_time > games_dict[game_name]['maxPlayTime']:
            games_dict[game_name]['maxPlayTime'] = play_time
            games_dict[game_name]['lastPlayed'] = row['lastPlayed']

        if account_id not in accounts:
            accounts[account_id] = {
                'id': account_id,
                'accountName': row['accountName'],
                'platform': row['platform'],
                'accountid': row['accountid']
            }

    print("Games and accounts processing complete")
    return list(games_dict.values()), list(accounts.values())

@index_router.get("/api/accounts")
async def accounts():
    return {"accounts": get_accounts()}

@index_router.get("/api/games")
async def index():
    games, accounts = get_games(False)
    return {"games": games, "accounts": accounts}

@index_router.get("/api/installed")
async def installed():
    games, accounts = get_games(True)
    return {"games": games, "accounts": accounts}

@index_router.get('/api/status')
def api_test():
    print("Status check requested")
    return {"status": "running", "message": "Server is operational"}

@index_router.get('/api/sync')
async def sync_games():
    print("Syncing games")
    update_games()
    return {"message": "Games synced"}

@index_router.get('/api/path')
async def steampath():
    print("Fetching Steam path")
    with open("static/locations.json", 'r') as f:
        return json.load(f)

@index_router.post("/api/path/update")
async def update_steampath(request: Request):
    try:
        data = await request.json()
        new_path = data.get('new_path')
        print(f"Updating Steam path to {new_path}")

        with open("static/locations.json", 'r+') as f:
            config = json.load(f)
            config["steampath"] = new_path
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()

        return {"message": "Steam path updated successfully", "new_path": new_path}
    except Exception as e:
        print(f"Error updating Steam path: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@index_router.post('/api/fav')
async def updategamespec(request: Request):
    data = await request.json()
    game_name = data.get('game_name')
    print(f"Updating favorite status for game: {game_name}")

    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO gamespec (game_name, fav)
            VALUES (?, ?) ON CONFLICT(game_name) DO UPDATE SET fav = NOT fav
        """, (game_name, True))
        db.commit()

    return {"message": "Database updated successfully"}

@index_router.get('/api/run/steam')
async def runsteam(steamid: str, appid: str | None = None):
    print(f"Starting Steam game with steamid={steamid}, appid={appid}")
    manager = SteamRun()
    manager.run(steamid=steamid, appid=appid)
    return {"message": "Game started"}
