from flask import Blueprint, render_template, redirect, url_for, request, jsonify
import sqlite3
from static.utils.update_games import update_games

index_bp = Blueprint('index_bp', __name__)


def get_games():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.execute("""
        SELECT games.*, accounts.id AS acc_id, accounts.accountName, accounts.platform, accounts.steamAPI, accounts.accountid,
               gamespec.fav, gamespec.completed
        FROM games
        LEFT JOIN accounts ON games.account_id = accounts.id
        LEFT JOIN gamespec ON games.GameName = gamespec.game_name
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

        if row['accountid'] not in [acc['accountid'] for acc in accounts]:
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

@index_bp.route("/api/games", methods=["GET"])
def index():
    games, accounts = get_games()
    return jsonify({"games": games, "accounts": accounts})
@index_bp.route('/api/test')
def api_test():
    return {"message": "API works!"}
@index_bp.route('/api/sync')
def sync_games():
    update_games()
    return "abc"
@index_bp.route('/api/fav', methods=['POST'])
def updategamespec():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    data = request.get_json()
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
    return jsonify({'message': 'Database updated successfully'})