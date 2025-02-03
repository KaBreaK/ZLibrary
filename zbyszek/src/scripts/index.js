
const searchInput = document.getElementById('search-input');
const searchIcon = document.getElementById('search-icon');
const clearIcon = document.getElementById('clear-icon');
const searchIconImg = document.getElementById('search-icon-img');
const clearIconImg = document.getElementById('clear-icon-img');
let gamesData
clearIcon.addEventListener('click', () => {
    searchInput.value = '';
    clearIcon.style.display = 'none';
    searchIcon.style.display = 'inline-block';
});
searchInput.addEventListener('input', () => {
    if (searchInput.value) {
        clearIcon.style.display = 'inline-block';
    } else {
        clearIcon.style.display = 'none';
    }
});
async function fetchGames() {
    try {
        const response = await fetch('http://localhost:8090/api/games');
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching games:', error);
        return { games: [] };
    }
}
async function fetchInstalledGames(a) {
    try {
        const response = await fetch('http://localhost:8090/api/installed');
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching games:', error);
        return { games: [] };
    }
}
function displayGames(games) {
    const gamesContainer = document.getElementById('games');
    gamesContainer.innerHTML = '';

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    games.forEach(game => {
        const gameItem = document.createElement('div');
        gameItem.classList.add('game-item');
        if (!game.installed) {
            gameItem.classList.add('not-installed');
        }
        const gameImage = document.createElement('img');
        gameImage.src = game.gamephoto;
        gameImage.onerror = function() {
            this.onerror = null;
            this.src = `C:\\Program Files (x86)\\Steam\\appcache\\librarycache\\${game.steamid}\\library_600x900.jpg`;
        };
        gameImage.alt = game.name;

        const playButton = document.createElement('button');
        playButton.classList.add('play-button');
        playButton.innerHTML = '▶';
        playButton.onclick = () => {choose(game)}
        const overlay = document.createElement('div');
        overlay.classList.add('overlay');

        const gameName = document.createElement('div');
        gameName.classList.add('game-name');
        gameName.textContent = game.name;

        const timeContainer = document.createElement('div');
        timeContainer.classList.add('time-container');

        const totalTime = document.createElement('div');
        totalTime.classList.add('total-time');
        totalTime.textContent = `Total: ${Math.floor(game.totalPlayTime / 60)}h`;

        const accountsTime = document.createElement('div');
        accountsTime.classList.add('accounts-time');
        accountsTime.innerHTML = game.playTimePerAccount.map(account =>
            `<div>${account.accountName}: ${Math.floor(account.playTime / 60)}h</div>`
        ).join('');

        overlay.appendChild(gameName);
        overlay.appendChild(playButton);
        timeContainer.appendChild(totalTime);
        timeContainer.appendChild(accountsTime);

        gameItem.appendChild(gameImage);
        gameItem.appendChild(overlay);
        gameItem.appendChild(timeContainer);
        gamesContainer.appendChild(gameItem);
        observer.observe(gameItem);
    });
}
function sortGames(games, sortOption) {
    switch (sortOption) {
        case 1: // Alfabetycznie
            return games.sort((a, b) => a.name.localeCompare(b.name));
        case 2: // Alfabetycznie odwrotnie
            return games.sort((a, b) => b.name.localeCompare(a.name));
        case 3: // Po czasie gry malejąco
            return games.sort((a, b) => b.totalPlayTime - a.totalPlayTime);
        case 4: // Po czasie gry rosnąco
            return games.sort((a, b) => a.totalPlayTime - b.totalPlayTime);
        case 5: // Ostatnio zagrane (0 lub none na końcu)
            return games.sort((a, b) => {
                if (a.lastPlayed === 0 || a.lastPlayed === null) return 1;
                if (b.lastPlayed === 0 || b.lastPlayed === null) return -1;
                return b.lastPlayed - a.lastPlayed;
            });
        case 6:
            return games.sort((a, b) => {
                if (a.lastPlayed === 0 || a.lastPlayed === null) return 1;
                if (b.lastPlayed === 0 || b.lastPlayed === null) return -1;
                return b.lastPlayed - a.lastPlayed;
            });
        case 7:
            return games.sort((a, b) => {
                const priorityA = (a.fav ? 0 : 1) + (a.installed ? 0 : 2);
                const priorityB = (b.fav ? 0 : 1) + (b.installed ? 0 : 2);

                if (priorityA !== priorityB) {
                    return priorityA - priorityB;
                } else {
                    return a.name.localeCompare(b.name);
                }
            });
        default:
            return games;
    }
}
;


document.getElementById('sortTrigger').addEventListener('click', function(event) {
    event.stopPropagation();
    document.getElementById('sortModal').style.display = 'block';
});
document.addEventListener('click', function(event) {
    const modal = document.getElementById('sortModal');
    if (event.target !== modal && !modal.contains(event.target)) {
        modal.style.display = 'none';
    }
});
document.querySelectorAll('.sort-option').forEach(option => {
    option.addEventListener('click', function() {
        const sortOption = parseInt(this.getAttribute('data-sort'));
        displayGames(sortGames(gamesData.games, sortOption));
        document.getElementById('sortModal').style.display = 'none';
    });
});
document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');

    if (action === "library") {
        gamesData = await fetchGames();
        displayGames(sortGames(gamesData.games, 7));
    } else if (action === "installed") {
        gamesData = await fetchInstalledGames();
        displayGames(sortGames(gamesData.games, 7));
    }else{
        gamesData = await fetchGames();
        displayGames(sortGames(gamesData.games, 7));
    }
});
async function choose(game) {
    const container = document.getElementById('accountchooser');

    if (game.playTimePerAccount.length === 1) {
        const account = game.playTimePerAccount[0];
        launch(account.platform, game.steamid)
        return;
    }

    container.style.display = 'block';
    container.innerHTML = `
        <h2 style="color: #FFFFFF; margin-bottom: 15px; text-align: center; margin-top: 0px">
            Choose Account
        </h2>
    `;

    game.playTimePerAccount.forEach(account => {
        const accountDiv = document.createElement('div');
        accountDiv.classList.add('account-item');
        accountDiv.innerHTML = `
            <img src="../images/${account.platform}.png" height="1%">
            <h4>${account.accountName}</h4>
        `;
        accountDiv.addEventListener('click', (event) => {
            launch(account.platform, game.steamid)
            event.stopPropagation();
        });
        container.appendChild(accountDiv);
    });
    function closeChooser(event) {
        if (!container.contains(event.target)) {
            container.style.display = 'none';
            document.removeEventListener('click', closeChooser);
        }
    }
    setTimeout(() => {
        document.addEventListener('click', closeChooser);
    }, 0);
}

const handleSearch = () => {
  const searchTerm = searchInput.value.toLowerCase();
  const filtered = gamesData.games.filter(game =>
    game.name.toLowerCase().includes(searchTerm)
  );
  displayGames(filtered);
  clearIcon.style.display = searchTerm ? 'block' : 'none';
};

searchInput.addEventListener('input', handleSearch);

clearIcon.addEventListener('click', () => {
  searchInput.value = '';
  displayGames(gamesData.games);
  clearIcon.style.display = 'none';
});
