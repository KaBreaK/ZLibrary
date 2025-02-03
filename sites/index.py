from fastapi import APIRouter, HTTPException, Request
import sqlite3
from static.utils.update_games import update_games
import json
index_router = APIRouter()

def get_accounts():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("SELECT * FROM accounts")

    rows = cursor.fetchall()

    accounts = []

    for row in rows:
        accounts.append({
            'id': row['id'],
            'accountName': row['accountName'],
            'platform': row['platform'],
            'steamAPI': row['steamAPI'],
            'accountid': row['accountid']
        })

    return accounts

def get_games(b):
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(f"""
        SELECT games.*, accounts.id AS acc_id, accounts.accountName, accounts.platform, accounts.steamAPI, accounts.accountid,
               gamespec.fav, gamespec.completed
        FROM games
        LEFT JOIN accounts ON games.account_id = accounts.id
        LEFT JOIN gamespec ON games.GameName = gamespec.game_name
        {"WHERE games.installed = 1" if b else ""}
    """)

    rows = cursor.fetchall()

    games_dict = {}
    accounts = []

    for row in rows:
        game_name = row['GameName']

        game_data = {
            'epicRunUrl': row['epicRunUrl'],
            'steamid': row['steamid'],
            'gamephoto': row['gamePhoto'],
            'account_id': row['account_id'],
            'playTime': row['playTime'],
            'lastPlayed': row['lastPlayed'],
            'installed': row['installed'] if row['installed'] is not None else 0,
            'fav': row['fav'] if row['fav'] is not None else 0,
            'completed': row['completed'] if row['completed'] is not None else 0,
            'accountName': row['accountName'],
            'platform': row['platform'],
            'accountid': row['accountid']
        }

        if game_name in games_dict:
            games_dict[game_name]['totalPlayTime'] += game_data['playTime']
            games_dict[game_name]['playTimePerAccount'].append({
                'accountName': game_data['accountName'],
                'platform': game_data['platform'],
                'playTime': game_data['playTime']
            })
            if game_data['playTime'] > games_dict[game_name]['maxPlayTime']:
                games_dict[game_name]['maxPlayTime'] = game_data['playTime']
                games_dict[game_name]['lastPlayed'] = game_data['lastPlayed']
        else:
            games_dict[game_name] = {
                'name': game_name,
                'epicRunUrl': game_data['epicRunUrl'],
                'steamid': game_data['steamid'],
                'gamephoto': game_data['gamephoto'],
                'totalPlayTime': game_data['playTime'],
                'lastPlayed': game_data['lastPlayed'],
                'installed': row['installed'] if row['installed'] is not None else 0,
                'fav': game_data['fav'],
                'completed': game_data['completed'],
                'playTimePerAccount': [{
                    'accountName': game_data['accountName'],
                    'platform': game_data['platform'],
                    'playTime': game_data['playTime']
                }],
                'maxPlayTime': game_data['playTime']
            }

        if row['acc_id'] not in [acc['id'] for acc in accounts]:
            account_data = {
                'id': row['acc_id'],
                'accountName': row['accountName'],
                'platform': row['platform'],
                'accountid': row['accountid']
            }

            accounts.append(account_data)

    db.commit()
    db.close()

    games = list(games_dict.values())

    return games, accounts

@index_router.get("/api/accounts")
def accounts():
    accounts = get_accounts()
    return {"accounts": accounts}

@index_router.get("/api/games")
def index():
    games, accounts = get_games(False)
    return {"games": games, "accounts": accounts}
@index_router.get("/api/installed")
def installed():
    games, accounts = get_games(True)
    return {"games": games, "accounts": accounts}
@index_router.get('/api/status')
def api_test():
    return {
        "status": "running",
        "message": "Server is operational"
    }

@index_router.get('/api/sync')
def sync_games():
    update_games()
    return {"message": "Games synced"}
@index_router.get('/api/path')
def steampath():
    with open("static/locations.json", 'r') as f:
        config = json.load(f)
    return config
@index_router.post('/api/fav')
async def updategamespec(request: Request):
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    data = await request.json()
    game_name = data.get('game_name')
    cursor.execute("SELECT fav FROM gamespec WHERE game_name = ?", (game_name,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO gamespec (game_name, fav) VALUES (?, ?)", (game_name, True))
    else:
        current_fav = result[0]
        new_fav = not current_fav
        cursor.execute("UPDATE gamespec SET fav = ? WHERE game_name = ?", (new_fav, game_name))
    db.commit()
    db.close()
    return {"message": "Database updated successfully"}