// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  loginViaSteam: () => ipcRenderer.invoke('LoginViaSteam')
});
contextBridge.exposeInMainWorld('electron', {
  loginViaEpic: () => ipcRenderer.invoke('LoginViaEpic')
});
contextBridge.exposeInMainWorld('electron', {
  loginViaEpic: () => ipcRenderer.invoke('LoginViaEA')
});
contextBridge.exposeInMainWorld('electron', {
  close: () => ipcRenderer.invoke('close')
});
contextBridge.exposeInMainWorld('electron', {
  minimize: () => ipcRenderer.invoke('minimize')
});
contextBridge.exposeInMainWorld('launch', {
  launch: (platform, appid) => ipcRenderer.invoke('launch', platform, appid)
});
