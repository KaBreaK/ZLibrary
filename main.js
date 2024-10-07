const { app, BrowserWindow, screen, Tray, Menu, ipcMain} = require('electron');
const { spawn } = require('child_process');
const axios = require('axios'); // Add axios for HTTP requests
const path = require('path'); // To help with paths

let flaskProcess;
let mainWindow;
let tray;
let isQuitting = false; // Flaga kontrolująca zamykanie aplikacji

async function checkIfServerRunning() {
    try {
        await axios.get('http://localhost:3000/');
        return true; // Server is running
    } catch (error) {
        return false; // Server is not running
    }
}

async function startFlaskServer() {
    // Ensure you're using the correct Python executable
    //flaskProcess = spawn('python', ['app.py'], {
    //    stdio: 'inherit', // This will pass the output to the parent process
    //    cwd: path.join(__dirname) // Ensure that the working directory is set to the current directory
    //});

    // Listen for exit events
    flaskProcess.on('exit', (code, signal) => {
        console.log(`Flask process exited with code: ${code}, signal: ${signal}`);
        flaskProcess = null; // Clear reference to process when it exits
    });

    // Listen for any errors
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
        //await startFlaskServer();
    }

    mainWindow.loadURL('http://localhost:3000/');
    mainWindow.webContents.openDevTools();

    //zamykanieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
    ipcMain.handle('closeapp', async () => {
        closeappbutton();
    });
    function closeappbutton() {
        //killflask();
        mainWindow.hide();
    }



    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.key === 'F11') {
            event.preventDefault(); // Blokuje działanie klawisza F11
        }
    });

    mainWindow.on('close', (event) => {
        if (!isQuitting) { // Sprawdź, czy zamknięcie nie jest z system tray
            event.preventDefault();
            mainWindow.hide();
        }
    });
}

function createTrayIcon() {
    tray = new Tray('static/images/tray.png'); // Replace with your icon path
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Show', click: () => mainWindow.show() },
        { label: 'Quit', click: () => {
            isQuitting = true; // Ustaw flagę na true przy wybraniu "Quit"
            if (flaskProcess) {
                flaskProcess.kill(); // Kill the Flask process
            }
            app.quit();
        }},
    ]);

    tray.setToolTip('ZLibrary');
    tray.setContextMenu(contextMenu);
    tray.on('click', () => {
        mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
    });
}

// Ensure Flask process is killed when the app quits
app.on('before-quit', () => {
    isQuitting = true; // Ustaw flagę na true przy zamykaniu aplikacji
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
