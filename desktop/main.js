const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
function crea() {
  const w = new BrowserWindow({
    width: 1100, height: 850, minWidth: 380, minHeight: 500,
    title: 'Officina dell'Inventore', icon: path.join(__dirname, 'icon.png'),
    autoHideMenuBar: true, backgroundColor: '#E8EBEE',
    webPreferences: { contextIsolation: true }
  });
  w.webContents.setWindowOpenHandler(({ url }) => { shell.openExternal(url); return { action: 'deny' }; });
  w.loadFile(path.join(__dirname, 'www', 'index.html'));
}
app.whenReady().then(crea);
app.on('window-all-closed', () => app.quit());
