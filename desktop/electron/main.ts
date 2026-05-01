import { app, BrowserWindow, globalShortcut, ipcMain, systemPreferences, Tray, Menu, nativeImage, dialog, clipboard } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import Store from 'electron-store'
import { spawn } from 'child_process'
import fs from 'fs'
import os from 'os'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

interface StoreSchema {
  hotkey: string
  modelPath: string
  autoPaste: boolean
  audioDevice: string
  language: string
  showTrayIcon: boolean
  startMinimized: boolean
  meetingDetection: boolean
  detectedApps: string[]
}

const store = new Store<StoreSchema>({
  defaults: {
    hotkey: 'CommandOrControl+Shift+Space',
    modelPath: '',
    autoPaste: true,
    audioDevice: 'default',
    language: 'en',
    showTrayIcon: true,
    startMinimized: false,
    meetingDetection: true,
    detectedApps: ['zoom', 'teams', 'webex', 'skype', 'discord', 'chime'],
  },
})

let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null
let isRecording = false
let recordingProcess: any = null
let tempAudioPath = ''

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: !store.get('startMinimized'),
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  mainWindow.on('close', (event) => {
    if (store.get('showTrayIcon')) {
      event.preventDefault()
      mainWindow?.hide()
    }
  })
}

const createTray = () => {
  const iconPath = path.join(__dirname, '../assets/tray-icon.png')
  let trayIcon: Electron.NativeImage

  if (fs.existsSync(iconPath)) {
    trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 })
  } else {
    trayIcon = nativeImage.createEmpty()
  }

  tray = new Tray(trayIcon)
  tray.setToolTip('Transcribe Me')

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        mainWindow?.show()
        mainWindow?.focus()
      },
    },
    {
      label: isRecording ? 'Stop Recording' : 'Start Recording',
      click: () => {
        toggleRecording()
      },
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        mainWindow?.show()
        mainWindow?.webContents.send('navigate-to-settings')
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        globalShortcut.unregisterAll()
        app.quit()
      },
    },
  ])

  tray.setContextMenu(contextMenu)
  tray.on('click', () => {
    if (mainWindow?.isVisible()) {
      mainWindow.hide()
    } else {
      mainWindow?.show()
      mainWindow?.focus()
    }
  })
}

const toggleRecording = async () => {
  if (isRecording) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  if (isRecording) return

  const tmpDir = os.tmpdir()
  tempAudioPath = path.join(tmpDir, `recording-${Date.now()}.wav`)

  // Check microphone permission on macOS
  if (process.platform === 'darwin') {
    const status = systemPreferences.getMediaAccessStatus('microphone')
    if (status !== 'granted') {
      dialog.showErrorBox('Permission Required', 'Microphone access is required. Please grant permission in System Settings.')
      return
    }
  }

  isRecording = true
  mainWindow?.webContents.send('recording-started')
  updateTrayMenu()

  // Use sox or rec for recording
  const recCommand = process.platform === 'darwin' ? 'rec' : 'sox'
  recordingProcess = spawn(recCommand, [
    '-q',
    '-t', 'wav',
    '-r', '16000',
    '-c', '1',
    '-b', '16',
    '-e', 'signed-integer',
    tempAudioPath,
    'silence', '1', '0.1', '1%',
  ])

  recordingProcess.on('error', (error: Error) => {
    console.error('Recording error:', error)
    isRecording = false
    mainWindow?.webContents.send('recording-error', error.message)
    updateTrayMenu()
  })
}

const stopRecording = () => {
  if (!isRecording || !recordingProcess) return

  recordingProcess.kill('SIGTERM')
  isRecording = false
  mainWindow?.webContents.send('recording-stopped')
  updateTrayMenu()

  // Wait for file to be written then transcribe
  setTimeout(() => {
    if (fs.existsSync(tempAudioPath)) {
      transcribeAudio(tempAudioPath)
    }
  }, 500)
}

const transcribeAudio = async (audioPath: string) => {
  try {
    mainWindow?.webContents.send('transcription-started')

    const modelPath = store.get('modelPath')
    const language = store.get('language')

    if (!modelPath) {
      // Use Python backend with parakeet-mlx
      const pythonScript = path.join(__dirname, '../python/transcribe.py')
      const pythonProcess = spawn('python3', [
        pythonScript,
        audioPath,
        '--language', language,
      ])

      let transcript = ''
      pythonProcess.stdout.on('data', (data) => {
        transcript += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          handleTranscriptionResult(transcript.trim())
        } else {
          mainWindow?.webContents.send('transcription-error', 'Transcription failed')
        }
        cleanupAudioFile(audioPath)
      })
    } else {
      // Use local model
      const pythonScript = path.join(__dirname, '../python/transcribe_local.py')
      const pythonProcess = spawn('python3', [
        pythonScript,
        audioPath,
        '--model', modelPath,
        '--language', language,
      ])

      let transcript = ''
      pythonProcess.stdout.on('data', (data) => {
        transcript += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code === 0) {
          handleTranscriptionResult(transcript.trim())
        } else {
          mainWindow?.webContents.send('transcription-error', 'Transcription failed')
        }
        cleanupAudioFile(audioPath)
      })
    }
  } catch (error) {
    console.error('Transcription error:', error)
    mainWindow?.webContents.send('transcription-error', (error as Error).message)
    cleanupAudioFile(audioPath)
  }
}

const handleTranscriptionResult = (text: string) => {
  mainWindow?.webContents.send('transcription-result', text)

  if (store.get('autoPaste')) {
    clipboard.writeText(text)
    // Simulate paste on macOS
    if (process.platform === 'darwin') {
      const appleScript = `
        tell application "System Events"
          keystroke "v" using command down
        end tell
      `
      spawn('osascript', ['-e', appleScript])
    }
  }
}

const cleanupAudioFile = (audioPath: string) => {
  try {
    if (fs.existsSync(audioPath)) {
      fs.unlinkSync(audioPath)
    }
  } catch (error) {
    console.error('Cleanup error:', error)
  }
}

const updateTrayMenu = () => {
  if (!tray) return

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show App',
      click: () => {
        mainWindow?.show()
        mainWindow?.focus()
      },
    },
    {
      label: isRecording ? '⏹ Stop Recording' : '⏺ Start Recording',
      click: () => {
        toggleRecording()
      },
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        mainWindow?.show()
        mainWindow?.webContents.send('navigate-to-settings')
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        globalShortcut.unregisterAll()
        app.quit()
      },
    },
  ])

  tray.setContextMenu(contextMenu)
}

const registerHotkey = () => {
  const hotkey = store.get('hotkey')

  globalShortcut.unregisterAll()

  const registered = globalShortcut.register(hotkey, () => {
    toggleRecording()
  })

  if (!registered) {
    dialog.showErrorBox('Hotkey Error', `Failed to register hotkey: ${hotkey}. It may be in use by another application.`)
  }
}

// IPC handlers
ipcMain.handle('get-store-value', (_, key: keyof StoreSchema) => {
  return store.get(key)
})

ipcMain.handle('set-store-value', (_, key: keyof StoreSchema, value: any) => {
  store.set(key, value)
})

ipcMain.handle('toggle-recording', () => {
  toggleRecording()
})

ipcMain.handle('get-recording-status', () => {
  return isRecording
})

ipcMain.handle('select-model-path', async () => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openDirectory'],
    title: 'Select Model Directory',
  })

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0]
  }
  return null
})

ipcMain.handle('download-model', async (_, modelId: string) => {
  const pythonScript = path.join(__dirname, '../python/download_model.py')
  const pythonProcess = spawn('python3', [pythonScript, modelId])

  return new Promise((resolve, reject) => {
    let output = ''
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
      mainWindow?.webContents.send('download-progress', data.toString())
    })

    pythonProcess.stderr.on('data', (data) => {
      mainWindow?.webContents.send('download-progress', data.toString())
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(output.trim())
      } else {
        reject(new Error('Model download failed'))
      }
    })
  })
})

ipcMain.handle('detect-meeting-apps', () => {
  // Check for running meeting applications
  const detectedApps: string[] = []
  const appsToCheck = store.get('detectedApps')

  if (process.platform === 'darwin') {
    const script = `
      tell application "System Events"
        set appList to name of every process whose background only is false
        return appList
      end tell
    `
    const osaProcess = spawn('osascript', ['-e', script])
    let output = ''

    osaProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    osaProcess.on('close', () => {
      const runningApps = output.toLowerCase()
      appsToCheck.forEach((app) => {
        if (runningApps.includes(app.toLowerCase())) {
          detectedApps.push(app)
        }
      })
      mainWindow?.webContents.send('meeting-apps-detected', detectedApps)
    })
  }

  return detectedApps
})

// App event handlers
app.whenReady().then(() => {
  createWindow()
  createTray()
  registerHotkey()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})

app.on('before-quit', () => {
  if (isRecording) {
    stopRecording()
  }
})
