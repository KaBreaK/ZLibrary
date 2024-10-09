from flask import Blueprint, render_template, redirect, url_for, request, jsonify
import sqlite3
index_bp = Blueprint('index_bp', __name__)


def get_games():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Updated SQL query with LEFT JOIN to gamespec table
    cursor.execute("""
        SELECT games.*, accounts.id AS acc_id, accounts.accountName, accounts.platform, accounts.steamAPI, accounts.accountid,
               gamespec.fav, gamespec.completed
        FROM games
        LEFT JOIN accounts ON games.account_id = accounts.id
        LEFT JOIN gamespec ON games.GameName = gamespec.game_name
    """)

    rows = cursor.fetchall()

    games_dict = {}  # Dictionary to hold unique games with combined data
    accounts = []  # List to store account details

    for row in rows:
        game_name = row['GameName']

        # Set default values of 0 if fav or completed is None
        game_data = {
            'epicRunUrl': row['epicRunUrl'],
            'steamid': row['steamid'],
            'gamephoto': row['gamePhoto'],
            'account_id': row['account_id'],
            'playTime': row['playTime'],
            'lastPlayed': row['lastPlayed'],
            'fav': row['fav'] if row['fav'] is not None else 0,
            'completed': row['completed'] if row['completed'] is not None else 0,
            'accountName': row['accountName'],
            'platform': row['platform'],
            'accountid': row['accountid']
        }

        # If the game already exists in the games_dict, update the total playtime and lastPlayed logic
        if game_name in games_dict:
            games_dict[game_name]['totalPlayTime'] += game_data['playTime']
            games_dict[game_name]['playTimePerAccount'].append({
                'accountName': game_data['accountName'],
                'platform': game_data['platform'],
                'playTime': game_data['playTime']
            })
            # Update lastPlayed if the current playTime is higher
            if game_data['playTime'] > games_dict[game_name]['maxPlayTime']:
                games_dict[game_name]['maxPlayTime'] = game_data['playTime']
                games_dict[game_name]['lastPlayed'] = game_data['lastPlayed']
        else:
            # If game doesn't exist yet, add it with initial values
            games_dict[game_name] = {
                'name': game_name,
                'epicRunUrl': game_data['epicRunUrl'],
                'steamid': game_data['steamid'],
                'gamephoto': game_data['gamephoto'],
                'totalPlayTime': game_data['playTime'],
                'lastPlayed': game_data['lastPlayed'],
                'fav': game_data['fav'],
                'completed': game_data['completed'],
                'playTimePerAccount': [{
                    'accountName': game_data['accountName'],
                    'platform': game_data['platform'],
                    'playTime': game_data['playTime']
                }],
                'maxPlayTime': game_data['playTime']  # Keep track of max playtime to update lastPlayed
            }

        # Ensure account data is unique
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

    # Convert the games_dict back to a list
    games = list(games_dict.values())

    return games, accounts

@index_bp.route("/api/games", methods=["GET"])
def index():
    games, accounts = get_games()
    return jsonify({"games": games, "accounts": accounts})
@index_bp.route('/api/test')
def api_test():
    return {"message": "API works!"}