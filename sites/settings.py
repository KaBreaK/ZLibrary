from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, render_template_string
from urllib import parse
import re
import os
import sqlite3
import json
import time
from static.utils.Epic_games_library import EpicGamesStoreService
from static.utils.update_games import update_games
from static.utils.steam import get_steam_name
from static.utils.ea import EAAuthenticator
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


@settings_bp.route('/api/logout', methods=['GET'])
def delete_account():
    id = request.args.get('id')
    if not id:
        return "No account id provided", 400
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = ?', (id))
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
    service = EpicGamesStoreService("temp")
    games = service.run(auth)
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()
    with open('temp.egs.token', encoding="utf-8") as token_file:
        token = json.loads(token_file.read())
    name = token.get('displayName')
    print(name)
    cursor.execute('SELECT id FROM accounts WHERE platform = "EPIC" AND accountName = ?', (name,))
    results = cursor.fetchall()
    if not results:
        cursor.execute('INSERT INTO accounts (accountName, platform) VALUES (?, ?)', (name, "EPIC"))
        time.sleep(3)
        cursor.execute('SELECT id FROM accounts WHERE platform = "EPIC" AND accountName = ?', (name,))
    results = cursor.fetchall()
    if results:
        for row in results:
            account_id = row[0]
        token_path = f'{account_id}.egs.token'
        for game in games:
            cursor.execute('INSERT INTO games (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?,?)', (game['sandboxName'], game['runUrl'], (game['gameimage']), game['totalTime']/60, 0, account_id))
    if os.path.exists(token_path):
        os.remove(token_path)
    os.rename('temp.egs.token', token_path)
    db.commit()
    db.close()
    return jsonify({'success': True})

@settings_bp.route('/addpath', methods=['POST'])
def add_path():
    data = request.get_json()
    path = data.get('path')
    print(path)
    if path:
        print(path)
        return jsonify({'success': True})
    return jsonify({'success': False})


@settings_bp.route('/auth/ea', methods=['GET', 'POST'])
def loginea():
    if request.method == 'POST':
        db = sqlite3.connect("static/glibrary.db")
        cursor = db.cursor()
        login = request.form.get('login')
        password = request.form.get('password')



        cursor.execute('SELECT id FROM accounts WHERE platform = "EA" AND accountName = ?', (login,))
        results = cursor.fetchall()
        if not results:
            cursor.execute('INSERT INTO accounts (accountName, platform) VALUES (?, ?)', (login, "EA"))
            time.sleep(3)
            cursor.execute('SELECT id FROM accounts WHERE platform = "EA" AND accountName = ?', (login,))
            results = cursor.fetchall()
        if results:
            for row in results:
                account_id = row[0]
                EA = EAAuthenticator(f'{account_id}.ea.token', login, password)
                games = EA.get_games()
            for game in games:
                cursor.execute('INSERT INTO games (gameName, gamePhoto, playTime, lastPlayed, account_id) VALUES (?,?,?,?,?)', (game['GameName'], (game['gamePhoto']), game['playtime'], game['lastPlayed'], account_id))
        db.commit()
        db.close()
        return render_template_string(f"""
        <script>
            const {{ ipcRenderer }} = require('electron');
            ipcRenderer.invoke('login-success');
            window.close();
        </script>
    """)

    return """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Formularz Logowania</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap" rel="stylesheet">
    <style>
    body {
    font-family: "Outfit", serif;
    display: flex;
    justify-content: center; /* Center horizontally */
    align-items: center; /* Center vertically */
    height: 100vh;
    margin: 0;
    background-color: #f0f0f0;
}
.container {
    display: flex;
    justify-content: space-between;
    width: 95%;
}
.textbox {
    font-family: "Outfit", serif;
    width: 30%;
    padding: 20px;
    background-color: #f9f9f9;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    color: #333;
    border: 2px solid red; /* Red border for emphasis */
    transition: all 0.3s ease;
    font-size: 15px; /* Reduced font size */
}
.form-container {
    display: flex;
    flex-direction: column;
    justify-content: center; /* Wyśrodkowanie w pionie */
    align-items: center; /* Wyśrodkowanie w poziomie */
    width: 30%;
    padding: 20px;
    background-color: white;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    margin: 0 20px; /* Margin between columns */
    height: 100%; /* Zapewnia, że kontener zajmuje pełną wysokość */
}

.form-container input {
    width: 80%;
    padding: 10px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 16px;
}
.form-container button {
    width: 80%;
    padding: 10px;
    margin: 10px 0;
    border: none;
    border-radius: 5px;
    background-color: #007bff;
    color: white;
    font-size: 16px;
    cursor: pointer;
}
.form-container button:hover {
    background-color: #0056b3;
}

    </style>
</head>
<body>
    <div class="container">
        <div class="textbox">
            <p>Szanowni Państwo,</br>

Przepraszamy za konieczność podania adresu e-mail oraz hasła w naszej aplikacji. EA jest jedynym serwisem, który wymaga tych danych, a ich celem jest umożliwienie dostępu do funkcji serwisu oraz uzyskanie odpowiednich cookies. Zapewniamy, że dane te <strong>NIE SĄ</strong> nigdzie przechowywane.</br>

Dziękujemy za zrozumienie i przepraszamy za wszelkie niedogodności.</p>
        </div>
        <div class="form-container">
            <form method="POST">
                <input type="text" name="login" placeholder="EMAIL" />
                <input type="password" name="password" placeholder="Hasło" />
                <button type="submit">Zaloguj się</button>
            </form>
        </div>
        <div class="textbox">
            <p>Szanowni Państwo,</br>

Aby Aplikacja prawidłowo zczytałą dane, urządzenie musi być oznaczone jako zaufane. To znaczy, nie ma konieczności podawania kodu e-mail/sms/TOTP przy logowaniu.</br>

Zalecamy, aby być zalogowanym na aplikacji EA, aby mieć pewność, że wszystko działa prawidłowo.</br>

Dziękujemy za zrozumienie.</p>
        </div>
    </div>
</body>
</html>
"""