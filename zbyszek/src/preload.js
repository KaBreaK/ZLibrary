const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  loginViaSteam: () => ipcRenderer.invoke('LoginViaSteam'),
  loginViaEpic: () => ipcRenderer.invoke('LoginViaEpic'),
  loginViaEA: () => ipcRenderer.invoke('LoginViaEA'),
  close: () => ipcRenderer.invoke('close'),
  minimize: () => ipcRenderer.invoke('minimize'),
  addsteampath: () => ipcRenderer.invoke('addsteampath'),
  questionpage: () => ipcRenderer.invoke('questionpage')
});
