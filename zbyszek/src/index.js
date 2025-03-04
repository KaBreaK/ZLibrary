const {
  app,
  BrowserWindow,
  screen,
  Tray,
    shell,
  Menu,
  ipcMain,
  dialog,
} = require("electron");
const gotTheLock = app.requestSingleInstanceLock();
const { exec, spawn } = require("child_process");
const axios = require("axios");
const path = require("node:path");
const http = require("http");
//TODO: aplikacja sie wlacza po wywolaniu
if (require("electron-squirrel-startup")) {
  app.quit();
}
const exePath = path.join(__dirname, 'back.exe');
const childProcess = spawn(exePath);
childProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });
childProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
let backproces;
let mainWindow;
let tray;
let isQuitting = false;
const createWindow = () => {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  mainWindow = new BrowserWindow({
    width: Math.floor(width * 0.75),
    height: Math.floor(height * 0.75),
    y: Math.floor((height - Math.floor(height * 0.7)) / 2) + 0,
    resizable: false,
    transparent: true,
    frame: false,
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  // mainWindow.webContents.openDevTools()
  ipcMain.handle("addpath", async () => {
    createLoginWindow("addpath");
  });
  ipcMain.handle("LoginViaSteam", async () => {
    createLoginWindow("steam");
  });
  ipcMain.handle("LoginViaEpic", async () => {
    createLoginWindow("EPIC");
  });
  ipcMain.handle("LoginViaEA", async () => {
    createLoginWindow("EA");
  });
  ipcMain.handle("close", async () => {
    mainWindow.hide();
  });
  ipcMain.handle("minimize", async () => {
    mainWindow.minimize();
  });
  ipcMain.handle('addsteampath', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });
    if (result.canceled) {
        return { message: "Operation cancelled" };
    }
    const newPath = result.filePaths[0];
    console.log("Selected path:", newPath);
    try {
        const response = await fetch("http://localhost:8090/api/path/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_path: newPath })
        });
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error("Error:", error);
        return { error: error.message };
    }
});
if (!gotTheLock) {
  console.log("Another instance is already running. Exiting...");
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, "sites/index.html"));

  // Open the DevTools.
  // mainWindow.webContents.openDevTools();
};
function createTrayIcon() {
  tray = new Tray("icon.ico");
  const contextMenu = Menu.buildFromTemplate([
    { label: "Show", click: () => mainWindow.show() },
    {
      label: "Quit",
      click: () => {
        isQuitting = true;
        try {
          const response = axios.post("http://localhost:8090/shutdown");
        } catch (error) {
          console.error(`zerwano polaczenie `);
        }
        fetch("http://localhost:8090/shutdown")
        app.quit();
      },
    },
  ]);

  tray.setToolTip("ZLibrary");
  tray.setContextMenu(contextMenu);
  tray.on("click", () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
}
app.on("before-quit", () => {
  isQuitting = true;
  fetch("http://localhost:8090/shutdown")
});
// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    //app.quit();
  }
});
app.on("ready", async () => {
  await createWindow();
  createTrayIcon();
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
app.on("second-instance", () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});
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
    },
  });
  const session = loginWindow.webContents.session;

  await session.clearStorageData({ storages: ["cookies"] });
  if (platform === "addpath") {
    dialog
      .showOpenDialog(mainWindow, {
        properties: ["openDirectory"],
      })
      .then((result) => {
        if (result.canceled) return;
        console.log("Selected path:", result.filePaths[0]);
        fetch("http://localhost:8090/addpath", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ path: result.filePaths[0] }),
        });
        loginWindow.close();
      });
  }
  if (platform === "steam") {
    loginWindow.loadURL("http://localhost:8090/auth/steam");
  }
  if (platform === "EA") {
    loginWindow.loadURL('http://localhost:8090/auth/ea');
  }
  if (platform === "EPIC") {
    loginWindow.loadURL(
      "https://www.epicgames.com/id/login?redirectUrl=https%3A//www.epicgames.com/id/api/redirect%3FclientId%3D34a02cf8f4414e29b15921876da36f9a%26responseType%3Dcode"
    );
    loginWindow.webContents.on("will-redirect", (event, url) => {
      if (url.startsWith("https://www.epicgames.com/id/api/redirect?clientId")) {
        loginWindow.webContents
          .executeJavaScript(
            `
      (async () => {
        const response = await fetch("${url}");
        const data = await response.json();
        return data.authorizationCode;
      })();
    `
          )
          .then((authorizationCode) => {
            console.log("Authorization Code: ", authorizationCode);
            fetch("http://localhost:8090/auth/epic", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ authorizationCode: authorizationCode }),
            })
              .then((response) => response.json())
              .then((data) => console.log("Success:", data))
              .catch((error) => console.error("Error:", error));
            loginWindow.close();
          })
          .catch((err) => {
            console.error("Błąd podczas uzyskiwania kodu autoryzacji:", err);
          });

        event.preventDefault();
      }
    });
  }
  ipcMain.handle("login-success", async () => {
    loginWindow.close();
  });

  loginWindow.on("closed", () => {
    loginWindow = null;
  });
}
// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
