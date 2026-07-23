const { app, BrowserWindow } = require('electron');
function createWindow(){const win=new BrowserWindow({width:1200,height:800,backgroundColor:'#0f172a',webPreferences:{contextIsolation:true}});win.loadURL(process.env.VITE_DEV_SERVER_URL || 'http://127.0.0.1:5173');}
app.whenReady().then(createWindow);app.on('window-all-closed',()=>{if(process.platform!=='darwin')app.quit();});
