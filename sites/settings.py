from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, render_template_string
from urllib import parse
import re
import sys
import sqlite3
import json
import time
from static.utils.Epic_games_library import EpicGamesStoreService
from static.utils.update_games import update_games
from static.utils.steam import get_steam_name
settings_bp = Blueprint('settings', __name__)
steam_openid_url = 'https://steamcommunity.com/openid/login'

steam_id_re = re.compile('https://steamcommunity.com/openid/id/(.*?)$')

@settings_bp.route('/api/add_account/', methods=['POST'])
def add_account():
    data = request.get_json()
    steam_id = data.get('steam_id')
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM accounts WHERE accountid =?', (steam_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO accounts (accountid, platform, accountName) VALUES (?,?,?)', (steam_id, 'Steam', get_steam_name(steam_id),))
    db.commit()
    db.close()
    update_games()
    return redirect('/')


@settings_bp.route('/api/delete_account', methods=['POST'])
def delete_account():
    data = request.get_json()
    accountName = data.get('accountName')
    platform = data.get('platform')
    if not accountName or not platform:
        return "Account name or platform missing", 400
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    cursor.execute('DELETE FROM accounts WHERE accountName = ? AND platform = ?', (accountName, platform))
    db.commit()
    db.close()
    update_games()

    return redirect('/')


@settings_bp.route("/auth/steam")
def login():
    params = {
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://127.0.0.1:8090/authorize/steam',
        'openid.realm': 'http://127.0.0.1:8090'
    }

    param_string = parse.urlencode(params)
    auth_url = steam_openid_url + "?" + param_string
    return redirect(auth_url)
@settings_bp.route("/authorize/steam")
def authorize():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    match = steam_id_re.search(dict(request.args)['openid.identity'])
    steam_id = match.group(1)
    cursor.execute('SELECT COUNT(*) FROM accounts WHERE accountid = ?', (steam_id,))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO accounts (accountName, platform, accountid) VALUES (?, ?, ?)', (get_steam_name(steam_id), 'Steam', steam_id))
    session.modified = True
    db.commit()
    db.close()
    update_games()

    return render_template_string(f"""
        <script>
            const {{ ipcRenderer }} = require('electron');
            ipcRenderer.invoke('login-success');
            window.close();
        </script>
    """)


@settings_bp.route('/auth/egs', methods=['POST'])
def loginegs():
    data = request.get_json()
    auth = data['authorizationCode']
    print(auth)
    service = EpicGamesStoreService()
    games = service.run(auth)
    print(games)
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    with open('.egs.token', encoding="utf-8") as token_file:
        token = json.loads(token_file.read())
    name = token.get('displayName')
    print(name)
    cursor.execute('SELECT id FROM accounts WHERE platform = "EPIC"')
    results = cursor.fetchall()
    if not results:
        cursor.execute('INSERT INTO accounts (accountName, platform) VALUES (?, ?)', (name, "EPIC"))
        time.sleep(3)
        cursor.execute('SELECT id FROM accounts WHERE platform = "EPIC"')
    results = cursor.fetchall()
    if results:
        for row in results:
            account_id = row[0]
        for game in games:
            cursor.execute('INSERT INTO games (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?,?)', (game['sandboxName'], game['runUrl'], game['gameimage'], game['totalTime']/60, 0, account_id))

    db.commit()
    db.close()
    return jsonify({'success': True})

@settings_bp.route('/addpath', methods=['POST'])
def add_path():
    steam_path = request.form.get('steamPath')
    if steam_path:
        print(steam_path)
        return f"Ścieżka Steam to: {steam_path}"
    return "Nie wybrano żadnej ścieżki"
    return  jsonify({'success': True})