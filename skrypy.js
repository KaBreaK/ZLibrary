//zamykanie backendu
window.href('localhost:8090/shutdown')



//pobiranie gier z api
function GetGames() {
    fetch('http://localhost:8090/api/games')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .catch(error => {
        console.error('Błąd podczas pobierania danych:', error);
    });
}



//test api
function TestApi() {
    fetch('http://localhost:8090/api/test')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => console.log('Success:', data))
        .catch((error) => console.error('Error:', error));
}




//odswiezenie listy gier (pobranie ich n nowo i sprawdzeni czy sa zainstalowane)
function UpdateGamesList() {
    fetch('http://localhost:8090/api/test')
        .then(response =>{
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            console.log("odswiezono liste gier");
        });
}



//Dodanie gier do ulubionych
async function updateFavorite(gameName) {
    try {
        const response = await fetch('localhost:8090/api/fav', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                game_name: gameName,
            }),
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result.message);
        } else {
            console.error('Błąd podczas aktualizacji ulubionych gier:', response.status);
        }
    } catch (error) {
        console.error('Błąd sieci:', error);
    }
}




//dodawanie steamid do bazy danych
function addSteamId(steamid) {
    try {
        const response = await fetch('localhost:8090/api/add_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                steam_id: steamid,
            }),
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result.message);
        } else {
            console.error('Błąd podczas dodawanie steamid:', response.status);
        }
    } catch (error) {
        console.error('Błąd sieci:', error);
    }
}



//usutanie konta steam
async function addSteamId(accountName, platform) {
    try {
        const response = await fetch('localhost:8090/api/add_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                steam_id: accountName,
                platform: platform,
            }),
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result.message);
        } else {
            console.error('Błąd podczas usuwania steamid:', response.status);
        }
    } catch (error) {
        console.error('Błąd sieci:', error);
    }
}
