const { app, BrowserWindow, screen, Tray, Menu, ipcMain } = require('electron');
const { exec, spawn } = require('child_process');
const axios = require('axios');
const path = require('path');

let flaskProcess;
let mainWindow;
let tray;
let isQuitting = false;

async function checkIfServerRunning() {
    try {
        await axios.get('http://localhost:8090/');
        return true;
    } catch (error) {
        return false;
    }
}

async function startFlaskServer() {
    flaskProcess = spawn('python', ['app.py'], {
        stdio: 'inherit',
        cwd: path.join(__dirname)
    });
    flaskProcess.on('exit', (code, signal) => {
        console.log(`Flask process exited with code: ${code}, signal: ${signal}`);
        flaskProcess = null;
    });
    flaskProcess.on('error', (error) => {
        console.error(`Failed to start Flask process: ${error.message}`);
    });
}
async function startFlaskServerRun() {
    exec("waitress-serve --port=8090 app:app")
    flaskProcess.on('exit', (code, signal) => {
        mainWindow.loadURL('http://localhost:8090/shutdown');
    });
    flaskProcess.on('error', (error) => {
        console.error(`Failed to start Flask process: ${error.message}`);
    });
}

async function createWindow() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;

    mainWindow = new BrowserWindow({
        width: Math.floor(width * 0.8),
        height: Math.floor(height * 0.8),
        x: Math.floor((width - width * 0.73) / 2),
        y: Math.floor((height - height * 0.55) / 2),
        transparent: true,
        frame: true,
        resizable: true,
        hasShadow: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });


    const serverRunning = await checkIfServerRunning();
    if (!serverRunning) {
        await startFlaskServer();
        //await startFlaskServerRun();
    }

    //mainWindow.loadURL('http://localhost:8090/');
    mainWindow.loadURL('http://localhost:8091/');
    mainWindow.webContents.openDevTools();

    //zamykanieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
    ipcMain.handle('closeapp', async () => {
        closeappbutton();
    });
    ipcMain.handle('LoginViaSteam', async () => {
        createLoginWindow('steam')
    });
    function closeappbutton() {
        //killflask();
        mainWindow.hide();
    }



    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.key === 'F11') {
            event.preventDefault();
        }
    });

    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
}
async function createLoginWindow(platform) {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;

    loginWindow = new BrowserWindow({
        width: Math.floor(width * 0.4),
        height: Math.floor(height * 0.5),
        x: Math.floor((width - width * 0.4) / 2),
        y: Math.floor((height - height * 0.5) / 2),
        transparent: true,
        frame: true,
        resizable: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });
    const session = loginWindow.webContents.session;

    await session.clearStorageData({ storages: ['cookies'] });
    if (platform === 'steam') {
        loginWindow.loadURL('http://localhost:8090/auth/steam');
    }
    if (platform === 'EPIC') {
        loginWindow.loadURL('https://www.epicgames.com/id/login?redirectUrl=https%3A//www.epicgames.com/id/api/redirect%3FclientId%3D34a02cf8f4414e29b15921876da36f9a%26responseType%3Dcode');
        loginWindow.webContents.on('will-redirect', (event, url) => {
            if (url.startsWith('https://www.epicgames.com/id/api/')) {
                // Przechwycenie kodu autoryzacji z odpowiedzi JSON
                loginWindow.webContents.executeJavaScript(`
      (async () => {
        const response = await fetch("${url}");
        const data = await response.json();
        return data.authorizationCode;
      })();
    `).then(authorizationCode => {
                    console.log("Authorization Code: ", authorizationCode);

                    // Wysłanie kodu autoryzacji do serwera Flask za pomocą POST
                    fetch('http://localhost:8090/auth/egs', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ authorizationCode: authorizationCode })
                    })
                        .then(response => response.json())
                        .then(data => console.log('Success:', data))
                        .catch((error) => console.error('Error:', error));

                    // Zamknięcie okna logowania
                    loginWindow.close();
                }).catch(err => {
                    console.error("Błąd podczas uzyskiwania kodu autoryzacji:", err);
                });

                event.preventDefault();
            }
        });
    }
    ipcMain.handle('login-success', async () => {
        loginWindow.close();
    });

    loginWindow.on('closed', () => {
        loginWindow = null;
    });
}
function createTrayIcon() {
    tray = new Tray('static/images/tray.png');
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show', click: () => mainWindow.show() },
        {
            label: 'Quit', click: () => {
                isQuitting = true;
                if (flaskProcess) {
                    flaskProcess.kill();
                }
                app.quit();
            }
        },
    ]);

    tray.setToolTip('ZLibrary');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    });
}
app.on('before-quit', () => {
    isQuitting = true;
    if (flaskProcess) {
        flaskProcess.kill();
    }
});

app.on('ready', async () => {
    await createWindow();
    createTrayIcon();

});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        //app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
