const { ipcRenderer } = require('electron');
const bodys = document.getElementById('mainpage')
let currentIndex = 0;
const increment = 8;
let search = document.getElementById('searchgame');
let gamescounter = 0;
let uniqueGameIds = new Set();
let abc = document.getElementById('abc');
let timespend = document.getElementById('timespend');
let lastplayed = document.getElementById('lastplayed');
const gamesfieldcounter = document.getElementById('liczbagier');
let endindex = 7
const cleararea = document.getElementById('clear');
const chooseaccount = document.getElementById('chooseaccount');
// Funkcja do grupowania gier i zarządzania kontami
function groupGamesAndAccounts(games, gamesspec, accounts) {
    const groupedGames = {};

    games.forEach(game => {
        const gameTime = Number(game.playTime) || 0;

        if (!groupedGames[game.name]) {
            const  gameSpecEntry = gamesspec.find(g => g.game_name === game.name);
            groupedGames[game.name] = {
                name: game.name,
                steamid: game.steamid,
                gameplaytime: 0,
                lastplayed: game.lastplayed,
                gamephoto: game.gamephoto,
                epicRunUrl: game.epicRunUrl,
                fav: gameSpecEntry ? gameSpecEntry.fav : 0,
                completed: gameSpecEntry ? gameSpecEntry.completed : 0,
                accounts: {}
            };
        }

        groupedGames[game.name].gameplaytime += gameTime;
        if (!groupedGames[game.name].accounts[game.account_id]) {
            groupedGames[game.name].accounts[game.account_id] = {
                name: accounts.find(acc => acc.id === game.account_id).accountName,
                platform: accounts.find(acc => acc.id === game.account_id).platform,
                totalGameplaytime: 0
            };
        }
        groupedGames[game.name].accounts[game.account_id].totalGameplaytime += gameTime;
        groupedGames[game.name].epicRunUrl = game.epicRunUrl;
        if (game.lastplayed > groupedGames[game.name].lastplayed) {
            groupedGames[game.name].lastplayed = game.lastplayed;
        }
    });

    return groupedGames;
}

const groupedGames = groupGamesAndAccounts(games, gamespec, accounts);

function closeApp() {
    ipcRenderer.invoke('closeapp').then(() => {
    console.log('Application closed successfully');
    }).catch((error) => {
    console.error('Failed to close application:', error);
});
}

function handleImageError(img, id) {
    img.onerror = null;

    img.src = 'https://cdn.akamai.steamstatic.com/steam/apps/' + id + '/capsule_467x181.jpg';
    let photos = img.parentNode;
    let div = photos.parentNode;
    div.style.backgroundImage = 'url("https://cdn.akamai.steamstatic.com/steam/apps/' + id + '/capsule_467x181.jpg")';
    div.style.backgroundSize = 'cover';
    div.style.backgroundPosition = 'center';
    img.style.borderRadius = "0px";
    img.removeAttribute('height');
    img.removeAttribute('width');

}

function epochToPolishDate(epochSeconds) {
    let date = new Date(epochSeconds * 1000);
    let options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        timeZone: 'Europe/Warsaw'
    };
    if (epochSeconds === 0 || epochSeconds === null){
        return "NIEZNANE";
    }else {
        return date.toLocaleDateString('pl-PL', options);
    }
}
function opensteam(steamid, account) {
    try {
        console.log(steamid + account)
        const result = ipcRenderer.invoke('opensteam', steamid, account);
        console.log('Steam launched:', result);
    } catch (error) {
        console.error('Błąd podczas uruchamiania Steam:', error.message);
    }
}
function loadMoreGames(sortedGames) {
    gamesfieldcounter.innerHTML = `${sortedGames.length} gier`;
    let btime = 1
    const search = document.getElementById('searchgame');
    const container = document.getElementById('games-container');
    if (currentIndex === 0){
        container.innerHTML = '';
    }

    sortedGames.forEach((game, index) => {
        if (index < currentIndex){
            return;
        }
        if (search.value.trim() !== '' && !game.name.toLowerCase().includes(search.value.trim().toLowerCase())) {
            endindex++;
            btime--;
            return;
        }
        if (currentIndex > endindex){
            return;
        }
        currentIndex++;
        btime++;
        const gameDiv = document.createElement('div');
        gameDiv.id = `game-${game.steamid}`;
        gameDiv.className = 'game';
        gameDiv.style.opacity = '0';
        let completepath;
        let favpath;
        if (game.completed === 0) {
            completepath = "/static/images/notcompleted.svg"
        }else{
            completepath = "/static/images/completed.svg"
        }
        if (game.fav === 0) {
            favpath = "/static/images/staroff.png"
        }else{
            favpath = "/static/images/staron.png"
        }
        console.log(completepath)
        console.log(favpath)
        let gaccounts = '';
        let allacounts = []
        let allplatforms = []
        Object.values(game.accounts).forEach(account => { gaccounts += ('<div class="timeperaccount">' + imgsrc(account.platform) + account.name + ' - ' + formatGameplayTime(account.totalGameplaytime) + '</div>'); allacounts.push(account.name);allplatforms.push(account.platform);});
        gameDiv.innerHTML = `
            <div class="game-image" id="game-background">
                <div class="photogame">
                    <img src="${game.gamephoto}" onerror="handleImageError(this, ${game.steamid})" width="300" height="450" />
                </div>
                <div class="game-hover-overlay">
                    <div class="hoverheader">
                        <div class="complete" onclick="
                        if (${game.completed} === 0){
                            console.log('dodaje do ulubionych')
                            updateDatabase('${game.name}', 0, 1, 'c')
                        }
                        else{
                            updateDatabase('${game.name}', 0, 0, 'c')
                            console.log('usuwa z ulubionych')
                        }
                        "><img src="${completepath}" alt="notcompleted"></div>
                        <div class="favourite" onclick="
                        if (${game.fav} === 0){
                            console.log('dodaje do ulubionych')
                            updateDatabase('${game.name}', 1, 0, 'f')
                        }
                        else{
                            updateDatabase('${game.name}', 0, 0, 'f')
                            console.log('usuwa z ulubionych')
                        }
                        "><img src="${favpath}" alt="notcompleted"></div>
                    </div>
                    <div class="play" onclick="   
                    console.log(${allacounts.length})
                    if (${allacounts.length} === 1){
                        if ('${allplatforms[0]}' === 'EPIC'){
                           let newWindow = window.open('com.epicgames.launcher://apps/${game.epicRunUrl}?action=launch&silent=true', 'com.epicgames.launcher://apps/${game.epicRunUrl}?action=launch&silent=true', 'width=400,height=300');
                           setTimeout(function() {
                           newWindow.close();
                            }, 50);
                        }else if ('${allplatforms[0]}' === 'Steam'){
                            opensteam(${game.steamid}, '${allacounts[0]}')
                        }
                    }else{
                        console.log('uruchamiam multiplayer')
                        addacountfield(${game.steamid}, '${allacounts}', '${game.epicRunUrl}', '${allplatforms}')
                    }
        ">
        <img src="/static/images/play.png" alt="play"></div>
                    <div class="lastplayed">
                        <h3>Czas gry</h3>
                        <h3>${formatGameplayTime(game.gameplaytime)}</h3>
                    </div>
                    <div class="timespend">
                        <h4>Ostatnia gra: <br>${epochToPolishDate(game.lastplayed)}</h4>
                        ${gaccounts}
                    </div>
                </div>
            </div>
            <div class="game-title">
                <h3>${game.name}</h3>
            </div>
        `;
        console.log(allacounts);
        container.appendChild(gameDiv);

        // Efekt pojawiania się gry
        setTimeout(() => {
            gameDiv.style.opacity = '1';
            gameDiv.style.transition = 'opacity 0.5s ease-in-out';
        }, 200 * btime);
    });
    endindex+=8;
}
function imgsrc(platform){
    if (platform==='Steam'){
        return '<img src="/static/images/steam.png" alt="Ikona" width="22">'
    }
    else if (platform==='EPIC'){
        return '<img src="/static/images/egs.ico" alt="Ikona" width="22">'
    }
}
function addacountfield(steamid, aallaccounts, epicurl, platforms)   {
    abcaccounts = aallaccounts.split(',')
    console.log(abcaccounts)
    console.log(epicurl)
    console.log("usage")
    platform = platforms.split(',')
    chooseaccount.style.display = 'flex';
    chooseaccount.innerHTML = '<h1>Wybierz Konto</h1>';
    for(let i=0; i<abcaccounts.length;i++) {
        const accountfield = document.createElement('div');
        accountfield.id = `account-'${abcaccounts[i]}'`;
        accountfield.className = 'accountfield';
        accountfield.onclick = () => {
            if (platform[i] === 'Steam') {
                console.log(abcaccounts[i])
                opensteam(steamid, abcaccounts[i]);
            }else if(platform[i] === 'EPIC'){
                console.log(epicurl)
                let newWindow = window.open(`com.epicgames.launcher://apps/${epicurl}?action=launch&silent=true`, "com.epicgames.launcher://apps/${epicurl}?action=launch&silent=true", "width=400,height=300");
                console.log(`com.epicgames.launcher://apps/${epicurl}?action=launch&silent=true`)
                setTimeout(function() {
                    newWindow.close();
                }, 50);
            }
            chooseaccount.style.display = 'none';
        };
        accountfield.innerHTML = `
              ${abcaccounts[i]}
        `;
        chooseaccount.appendChild(accountfield)
    }

}
function formatGameplayTime(minutes) {
    if (minutes < 59) {
        if (minutes === 1) {
            return `${minutes} minuta`;
        } else if (minutes >= 2 && minutes <= 4) {
            return `${minutes} minuty`;
        } else if ((minutes % 10) >= 2 && (minutes % 10) <= 4) {
            return `${minutes} minuty`;
        } else {
            return `${minutes} minut`;
        }
    } else{
        if ((minutes / 60).toFixed(0) === 1) {
            return `${(minutes / 60).toFixed(0)} godzina`;
        } else if ((minutes / 60).toFixed(0) >= 2 && (minutes / 60).toFixed(0) <= 4) {
            return `${(minutes / 60).toFixed(0)} godziny`;
        } else if ((minutes / 60).toFixed(0) > 20 && ((minutes / 60).toFixed(0) % 10) >= 2 && ((minutes / 60).toFixed(0) % 10) <= 4) {
            return `${(minutes / 60).toFixed(0)} godziny`;
        } else {
            return `${(minutes / 60).toFixed(0)} godzin`;
        }
    }
}

const gamesContainer = document.getElementById('games-container');
gamesContainer.addEventListener('scroll', () => {
    if (gamesContainer.scrollTop + gamesContainer.clientHeight >= gamesContainer.scrollHeight - 50) {
        loadSortedGames(currentSortType);
    }
});

function ilewyszukanych(tekst) {
    let gamescounter = 0;
    for (let i = 0; i < Object.keys(groupedGames).length; i++) {
        if (groupedGames[Object.keys(groupedGames)[i]].name.toLowerCase().includes(tekst.toLowerCase())) {
            gamescounter++;
        }
    }
    return gamescounter;
}

function sortGroupedGames(groupedGames, sortType) {
    const sortedGames = Object.values(groupedGames);
    if (sortType === 'name') {
        sortedGames.sort((a, b) => {
            if (b.fav - a.fav !== 0) {
                return b.fav - a.fav;
            } else {
                return a.name.localeCompare(b.name);
            }
        });
    } else if (sortType === 'gameplaytime') {
        sortedGames.sort((a, b) => b.gameplaytime - a.gameplaytime);
    } else if (sortType === 'lastplayed') {
        sortedGames.sort((a, b) => b.lastplayed - a.lastplayed);
    }

    return sortedGames;
}

let currentSortType = 'name'; // Domyślne sortowanie po nazwie
loadSortedGames('name');
function loadSortedGames(sortType) {
    currentSortType = sortType;
    const sortedGames = sortGroupedGames(groupedGames, sortType);
    loadMoreGames(sortedGames);
    updateSortButtons(sortType); // Aktualizacja kolorów przycisków sortowania
}

function updateSortButtons(sortType) {
    // Resetowanie kolorów wszystkich przycisków
    abc.style.backgroundColor = 'transparent';
    timespend.style.backgroundColor = 'transparent';
    lastplayed.style.backgroundColor = 'transparent';

    // Ustawienie koloru dla aktywnego przycisku
    if (sortType === 'name') {
        abc.style.backgroundColor = 'rgb(128, 128, 128, 0.8)';
    } else if (sortType === 'gameplaytime') {
        timespend.style.backgroundColor = 'rgb(128, 128, 128, 0.8)';
    } else if (sortType === 'lastplayed') {
        lastplayed.style.backgroundColor = 'rgb(128, 128, 128, 0.8)';
    }
}
search.addEventListener('input', () => {
    if (search.value === ''){
        console.log('ssssss')
        cleararea.style.display = 'none';
    }
    else{
        cleararea.style.display = 'flex';
    }
    currentIndex = 0;
    gamescounter = ilewyszukanych(search.value.trim());

    loadSortedGames('name');
    gamesfieldcounter.innerHTML = `${gamescounter} gier`;
});

// Obsługa kliknięć na przyciskach sortowania
abc.addEventListener('click', () => {
    if (currentSortType !== 'name') {
        currentIndex = 0;
        loadSortedGames('name');
    }
});

timespend.addEventListener('click', () => {
    if (currentSortType !== 'gameplaytime') {
        currentIndex = 0;
        loadSortedGames('gameplaytime');
    }
});

lastplayed.addEventListener('click', () => {
    if (currentSortType !== 'lastplayed') {
        currentIndex = 0;
        loadSortedGames('lastplayed');
    }
});
cleararea.addEventListener('click', () => {
    cleararea.style.display = 'none';
    search.value = '';
    currentIndex = 0;
    gamescounter = Object.keys(groupedGames).length;

    loadSortedGames('name');
    gamesfieldcounter.innerHTML = `${gamescounter} gier`;
});

console.log(groupedGames)