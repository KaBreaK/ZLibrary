// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
const { contextBridge, ipcRenderer } = require('electron');

// Wyeksponowanie funkcji `LoginViaSteam` do renderera
contextBridge.exposeInMainWorld('electron', {
  loginViaSteam: () => ipcRenderer.invoke('LoginViaSteam')
});