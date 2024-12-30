const { ipcRenderer } = require('electron');

function GetGames() {
    fetch('http://localhost:8090/api/games')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        }).then(data => {
            console.log(data);
    })
        .catch(error => {
        console.error('Błąd podczas pobierania danych:', error);
    });
}
async function LoginViaSteam(){
          try {
            await ipcRenderer.invoke('LoginViaSteam');
            console.log("JESTEM")
          } catch (error) {
            console.error('Błąd podczas logowania przez Steam:', error);
          }
          GetAccount()
}

async function addpath(){
    try {
        await ipcRenderer.invoke('addpath');
        console.log("JESTEM")
    } catch (error) {
        console.error('Błąd podczas logowania przez Steam:', error);
    }

}
async function LoginViaEpic(){
    try {
        await ipcRenderer.invoke('LoginViaEpic');
        console.log("JESTEM")
    } catch (error) {
        console.error('Błąd podczas logowania przez EPIC:', error);
    }
    GetAccount()
}
async function LoginViaEA(){
          try {
            await ipcRenderer.invoke('LoginViaEA');
            console.log("JESTEM")
          } catch (error) {
            console.error('Błąd podczas logowania przez EA:', error);
          }
          GetAccount()
}
function LoginViaBattleNet(){}
function SyncGames(){
            fetch("http://localhost:8090/api/sync", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            }).then(response => {
                if (response.ok) {
                    console.log("Synchronizacja zakończona.");
                }
            })
}
function GetAccount() {
    fetch('http://localhost:8090/api/accounts')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        }).then(data => {
            const steamAcc = document.getElementById('steam-accounts');
            const epicAcc = document.getElementById('epic-accounts');
            const eaAcc = document.getElementById('ea-accounts');
            steamAcc.innerHTML = '';
            epicAcc.innerHTML = '';
            eaAcc.innerHTML = '';
            data.forEach(account => {
                const li = document.createElement('li');
                li.textContent = account.accountName;
                const logoutButton = document.createElement('button');
                logoutButton.textContent = 'Wyloguj';
                logoutButton.onclick = () => logoutAccount(account.id, li);
                li.appendChild(logoutButton);
                switch (account.platform) {
                    case 'Steam':
                        steamAcc.appendChild(li);
                        break;
                    case 'EPIC':
                        epicAcc.appendChild(li);
                        break;
                    case 'EA':
                        eaAcc.appendChild(li);
                        break;
                    default:
                        console.error('Unknown platform: ' + account.platform);
                }
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function logoutAccount(accountId, liElement) {
    fetch(`http://localhost:8090/api/logout?id=${accountId}`, { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            console.log(`Account with id ${accountId} logged out successfully`);
            liElement.remove();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

window.onload = GetAccount;

