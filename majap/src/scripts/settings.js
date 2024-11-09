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
}
function LoginViaEpic(){}
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
