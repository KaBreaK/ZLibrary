const {
  app,
  BrowserWindow,
  screen,
  Tray,
  Menu,
  ipcMain,
  dialog,
} = require("electron");
const { exec, spawn } = require("child_process");
const axios = require("axios");
const path = require("node:path");
const http = require("http");

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require("electron-squirrel-startup")) {
  app.quit();
}
let flaskProcess;
let mainWindow;
let tray;
let isQuitting = false;
async function startFlaskServer() {
  flaskProcess = spawn("python", ["app.py"], {
    cwd: "../",
    stdio: "inherit",
  });
  flaskProcess.on("error", (error) => {
    console.error(`Failed to start Flask process: ${error.message}`);
  });
}
const createWindow = () => {
  startFlaskServer();

  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    resizable: false,
    transparent: true,
    frame: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  ipcMain.handle("addpath", async () => {
    createLoginWindow("addpath");
  });
  ipcMain.handle("LoginViaSteam", async () => {
    createLoginWindow("steam");
  });
  ipcMain.handle("LoginViaEpic", async () => {
    createLoginWindow("EPIC");
  });
  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, "index.html"));

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
};
function createTrayIcon() {
  tray = new Tray("src/icon.png");
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
        if (flaskProcess) {
          flaskProcess.kill();
        }
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
  if (flaskProcess) {
    flaskProcess.kill();
  }
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
  if (platform === "EPIC") {
    loginWindow.loadURL(
      "https://www.epicgames.com/id/login?redirectUrl=https%3A//www.epicgames.com/id/api/redirect%3FclientId%3D34a02cf8f4414e29b15921876da36f9a%26responseType%3Dcode"
    );
    loginWindow.webContents.on("will-redirect", (event, url) => {
      if (url.startsWith("https://www.epicgames.com/id/api/")) {
        // Przechwycenie kodu autoryzacji z odpowiedzi JSON
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
            fetch("http://localhost:8090/auth/egs", {
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
