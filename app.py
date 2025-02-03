from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sites.index import index_router
from sites.settings import settings_router
import sqlite3
import os
import json


app = FastAPI()
app.include_router(index_router)
app.include_router(settings_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    db = sqlite3.connect("static/glibrary.db")
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `Accounts` (
        `id` INTEGER NOT NULL,
        `accountName` TEXT NOT NULL,
        `platform` TEXT NOT NULL,
        `steamAPI` TEXT,
        `accountid` TEXT,
        PRIMARY KEY (`id`)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `Games`(
        `GameName` TEXT NOT NULL,
        `epicRunUrl` TEXT,
        `steamid` INTEGER,
        `gamePhoto` TEXT,
        `playTime` INTEGER,
        `lastPlayed` INTEGER,
        `installed` BOOLEAN,
        `account_id` INTEGER NOT NULL,
        FOREIGN KEY (`account_id`) REFERENCES `Accounts` (`id`)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS `gamespec` (
        game_name TEXT PRIMARY KEY,
        fav BOOLEAN,
        completed BOOLEAN
    );
    ''')

    db.commit()
    db.close()
def init_json():
    # Sprawdź, czy plik już istnieje
    if os.path.exists("static/locations.json"):
        return

    # Definiowanie ścieżek do bibliotek
    library_paths = {
        "steampath": "C:/Program Files (x86)/Steam",
        "epicpath": "C:/ProgramData/Epic/EpicGamesLauncher",
        "eapath": "C:/Program Files (x86)/Origin Games"
    }

    # Zapisanie do pliku JSON
    with open("static/locations.json", 'w') as f:
        json.dump(library_paths, f, indent=4)
init_db()
init_json()
@app.post("/shutdown")
async def shutdown(background_tasks: BackgroundTasks):
    background_tasks.add_task(os._exit, 0)
    return {"message": "Server shutting down..."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)