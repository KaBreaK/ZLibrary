const { ipcRenderer } = require('electron');
document.getElementById('settings').onclick = function() {
    window.location.href='settings.html';
}
document.getElementById('info').onclick = function() {
    ipcRenderer.invoke('questionpage',);
    console.log("WYSLANE")
}
document.getElementById('close').onclick = async function close(){
    try {
        await ipcRenderer.invoke('close');
        console.log("JESTEM")
    } catch (error) {
        console.error('Błąd podczas logowania przez Steam:', error);
    }
}
document.getElementById('minimize').onclick = async function minimize(){
    try {
        await ipcRenderer.invoke('minimize');
        console.log("JESTEM")
    } catch (error) {
        console.error('Błąd podczas logowania przez Steam:', error);
    }
}
let lastSyncTime = 0;
async function sync() {
    const now = Date.now();
    if (now - lastSyncTime < 60000) {
        console.log("Czekaj, synchronizacja może być wykonana tylko raz na minutę.");
        return;
    }

    lastSyncTime = now;
    showLoader()
    await fetch('http://localhost:8090/api/sync', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    hideLoader()
    window.location.href = "index.html?action=library";
}
document.getElementById("library").onclick = () => {
    window.location.href = "index.html?action=library";
};

document.getElementById("installed").onclick = () => {
    window.location.href = "index.html?action=installed";
};
//TODO: add support for ea
async function launch(platform, app, accountid){
          try {
            console.log(platform, app, accountid);
            if (platform == "Steam") {
                const response = await fetch(`http://localhost:8090/api/run/steam/?steamid=${accountid}&appid=${app}`)
            }
            if (platform == "EPIC"){
                window.location.href = `com.epicgames.launcher://apps/${app}?action=launch&silent=true`;
            }
            container.style.display = 'none';
            console.log("JESTEM")
          } catch (error) {
            console.error('Błąd podczas logowania przez Steam:', error);
          }
}
async function addpathsteam(){
    try {
        await ipcRenderer.invoke('addsteampath',);
        console.log("ELOBENCNOWASCIEZKA")
    } catch (error) {
        console.error('Błąd podczas logowania przez Steam:', error);
    }
}
async function addpathepic(){
    try {
        await ipcRenderer.invoke('addepicpath',);
        console.log("ELOBENCNOWASCIEZKA")
    } catch (error) {
        console.error('Błąd podczas logowania przez epic:', error);
    }
}





function showLoader() {
    const loader = document.querySelector('.loader');
    const body = document.body;
    loader.style.display = 'grid';
    body.classList.add('loading');
}
function hideLoader() {
    const loader = document.querySelector('.loader');
    const body = document.body;
    loader.style.display = 'none';
    body.classList.remove('loading');
}