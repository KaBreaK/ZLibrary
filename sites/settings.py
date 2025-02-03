import json
import os
import json
from fastapi import FastAPI, Request, Response, Depends, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from urllib import parse
import sqlite3
import re
from typing import Dict, Optional

from pydantic import BaseModel

from static.utils.steam import SteamLibrary
from static.utils.Epic_games_library import EpicGamesStoreService
from static.utils.update_games import update_games
settings_router = APIRouter()

@settings_router.get('/find')
async def find_game():
    steam_manager = SteamLibrary()
    steam_manager.update_steam_ids()
    steam_manager.close()
    update_games()
    return {
        "status": "god"
    }
@settings_router.get("/auth/steam")
async def login_steam():
    steam_openid_url = 'https://steamcommunity.com/openid/login'
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
    return RedirectResponse(url=auth_url)


@settings_router.get("/authorize/steam")
async def authorize_steam(request: Request):
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()

    query_params: Dict[str, str] = dict(request.query_params)
    steam_id_re = re.compile('https://steamcommunity.com/openid/id/(.*?)$')
    match = steam_id_re.search(query_params['openid.identity'])

    if match:
        steam = SteamLibrary()
        steam_id = match.group(1)
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE accountid = ?', (steam_id,))
        print(steam_id)
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO accounts (accountName, platform, accountid) VALUES (?, ?, ?)',(steam.get_steam_name(steam_id), 'Steam', steam_id))
        db.commit()
        db.close()
        return Response(content=f"""
            <script>
                const {{ ipcRenderer }} = require('electron');
                ipcRenderer.invoke('login-success');
                window.close();
            </script>
        """, media_type="text/html")

    db.close()
    return Response(content=f"""
                <script>
                    const {{ ipcRenderer }} = require('electron');
                    ipcRenderer.invoke('login-success');
                    window.close();
                </script>
            """, media_type="text/html")
class AuthRequest(BaseModel):
    authorizationCode: str
class AuthResponse(BaseModel):
    success: bool
    account_id: Optional[int] = None
    error: Optional[str] = None

@settings_router.post('/auth/epic')
async def login_epic(request: Request):
    try:
        data = await request.json()
        auth_code = data.get('authorizationCode')
        if not auth_code:
            raise ValueError("Missing authorization code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        service = EpicGamesStoreService("temp")
        games = service.run(auth_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")

    try:
        with open('temp.egs.token', 'r', encoding='utf-8') as f:
            token = json.load(f)
            display_name = token.get('displayName')
            if not display_name:
                raise ValueError("Missing displayName in token")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid token file: {str(e)}")

    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()

    try:
        cursor.execute(
            'SELECT id FROM accounts WHERE platform = "EPIC" AND accountName = ?',
            (display_name,)
        )
        account = cursor.fetchone()

        if account:
            account_id = account[0]
        else:
            cursor.execute(
                'INSERT INTO accounts (accountName, platform) VALUES (?, ?)',
                (display_name, "EPIC")
            )
            account_id = cursor.lastrowid

        token_path = f'{account_id}.egs.token'

        for game in games:
            cursor.execute(
                '''INSERT OR IGNORE INTO games 
                (gameName, epicRunUrl, gamePhoto, playTime, lastPlayed, account_id)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    game.get('sandboxName'),
                    game.get('runUrl'),
                    game.get('gameimage'),
                    game.get('totalTime', 0) / 60,
                    0,
                    account_id
                )
            )

        if os.path.exists(token_path):
            os.remove(token_path)
        os.rename('temp.egs.token', token_path)

        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()

    return {"success": True, "account_id": account_id}