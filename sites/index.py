from flask import Blueprint, render_template, redirect, url_for, request, jsonify
import sqlite3
index_bp = Blueprint('index', __name__)


def get_games():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT games.*, accounts.id, accounts.accountName, accounts.platform, accounts.steamAPI, accounts.accountid FROM games LEFT JOIN accounts ON games.account_id = accounts.id")
    rows = cursor.fetchall()
    games = []
    accounts = []
    for row in rows:
        game_data = {
            'name': row['GameName'],
            'epicRunUrl': row['epicRunUrl'],
            'steamid': row['steamid'],
            'gamephoto': row['gamephoto'],
            'playTime': row['playTime'],
            'lastplayed': row['lastplayed'],
            'account_id': row['account_id']
        }
        games.append(game_data)
        if row['accountid'] not in [acc['accountid'] for acc in accounts]:
            account_data = {
                'id': row['id'],
                'accountName': row['accountName'],
                'platform': row['platform'],
                'accountid' : row['accountid']
            }
            accounts.append(account_data)
    db.commit()
    db.close()
    return games, accounts

def get_gamespec():
    db = sqlite3.connect("static/glibrary.db")
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT fav, completed, game_name  FROM gamespec")
    rows = cursor.fetchall()
    gamespec = []
    for row in rows:
        game_data = {
            'fav': row['fav'],
            'completed': row['completed'],
            'game_name': row['game_name'],
        }
        gamespec.append(game_data)
    db.commit()
    db.close()
    return gamespec

@index_bp.route('/')
def index():
    games, accounts = get_games()
    gamespec = get_gamespec()
    return render_template('index.html', games=games, accounts=accounts, gamespec=gamespec)


@index_bp.route('/updategamespec', methods=['POST'])
def updategamespec():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    data = request.get_json()
    game_name = data.get('game_name')
    fav = data.get('fav', 0)
    completed = data.get('completed', 0)
    what = data.get('what')
    if what == 'f':
        cursor.execute("SELECT COUNT(*) FROM gamespec WHERE game_name = ?", (game_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO gamespec (game_name, fav, completed) VALUES (?, ?, ?)", (game_name, fav, completed))
        else:
            cursor.execute("UPDATE gamespec SET fav=? WHERE game_name=?", (fav, game_name))
    else:
        cursor.execute("SELECT COUNT(*) FROM gamespec WHERE game_name = ?", (game_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO gamespec (game_name, fav, completed) VALUES (?, ?, ?)", (game_name, 0, completed))
        else:
            cursor.execute("UPDATE gamespec SET completed=? WHERE game_name=?", (completed, game_name))
    db.commit()
    db.close()
    return jsonify({'message': 'Database updated successfully'})
