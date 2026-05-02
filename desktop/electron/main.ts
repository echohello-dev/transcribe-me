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
  activeModelId: string
  autoPaste: boolean
  audioDevice: string
  language: string
  showTrayIcon: boolean
  startMinimized: boolean
  meetingDetection: boolean
  detectedApps: string[]
  cloudProvider: string
  openaiApiKey: string
  assemblyaiApiKey: string
  models: any[]
}

const store = new Store<StoreSchema>({
  defaults: {
    hotkey: 'CommandOrControl+Shift+Space',
    modelPath: '',
    activeModelId: 'parakeet-tdt-0.6b-v3',
    autoPaste: true,
    audioDevice: 'default',
    language: 'en',
    showTrayIcon: true,
    startMinimized: false,
    meetingDetection: true,
    detectedApps: ['zoom', 'teams', 'webex', 'skype', 'discord', 'chime'],
    cloudProvider: '',
    openaiApiKey: '',
    assemblyaiApiKey: '',
    models: [],
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
  updateTrayMenu()

  tray.on('click', () => {
    if (mainWindow?.isVisible()) {
      mainWindow.hide()
    } else {
      mainWindow?.show()
      mainWindow?.focus()
    }
  })
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

  setTimeout(() => {
    if (fs.existsSync(tempAudioPath)) {
      transcribeAudio(tempAudioPath)
    }
  }, 500)
}

const transcribeAudio = async (audioPath: string) => {
  try {
    mainWindow?.webContents.send('transcription-started')

    const activeModelId = store.get('activeModelId')
    const language = store.get('language')
    const cloudProvider = store.get('cloudProvider')

    // Use cloud provider if selected
    if (cloudProvider && !activeModelId.startsWith('local-')) {
      await transcribeWithCloud(audioPath, cloudProvider, language)
      return
    }

    // Use local model
    const model = store.get('models').find((m: any) => m.id === activeModelId)
    const modelRepo = model?.hfRepo || 'mlx-community/parakeet-tdt-0.6b-v3'

    const pythonScript = path.join(__dirname, '../python/transcribe.py')
    const pythonProcess = spawn('python3', [
      pythonScript,
      audioPath,
      '--model', modelRepo,
      '--language', language,
    ])

    let output = ''
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.trim())
          handleTranscriptionResult(result)
        } catch {
          handleTranscriptionResult({ text: output.trim() })
        }
      } else {
        mainWindow?.webContents.send('transcription-error', 'Transcription failed')
      }
      cleanupAudioFile(audioPath)
    })
  } catch (error) {
    console.error('Transcription error:', error)
    mainWindow?.webContents.send('transcription-error', (error as Error).message)
    cleanupAudioFile(audioPath)
  }
}

const transcribeWithCloud = async (audioPath: string, provider: string, language: string) => {
  if (provider === 'openai') {
    const apiKey = store.get('openaiApiKey')
    if (!apiKey) {
      mainWindow?.webContents.send('transcription-error', 'OpenAI API key not configured')
      return
    }

    const pythonScript = path.join(__dirname, '../python/transcribe_cloud.py')
    const pythonProcess = spawn('python3', [
      pythonScript,
      audioPath,
      '--provider', 'openai',
      '--api-key', apiKey,
      '--language', language,
    ])

    let output = ''
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        handleTranscriptionResult({ text: output.trim() })
      } else {
        mainWindow?.webContents.send('transcription-error', 'OpenAI transcription failed')
      }
      cleanupAudioFile(audioPath)
    })
  } else if (provider === 'assemblyai') {
    const apiKey = store.get('assemblyaiApiKey')
    if (!apiKey) {
      mainWindow?.webContents.send('transcription-error', 'AssemblyAI API key not configured')
      return
    }

    const pythonScript = path.join(__dirname, '../python/transcribe_cloud.py')
    const pythonProcess = spawn('python3', [
      pythonScript,
      audioPath,
      '--provider', 'assemblyai',
      '--api-key', apiKey,
      '--language', language,
    ])

    let output = ''
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.trim())
          handleTranscriptionResult(result)
        } catch {
          handleTranscriptionResult({ text: output.trim() })
        }
      } else {
        mainWindow?.webContents.send('transcription-error', 'AssemblyAI transcription failed')
      }
      cleanupAudioFile(audioPath)
    })
  }
}

const handleTranscriptionResult = (result: any) => {
  mainWindow?.webContents.send('transcription-result', result)

  if (store.get('autoPaste') && result.text) {
    clipboard.writeText(result.text)
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

const registerHotkey = () => {
  const hotkey = store.get('hotkey')
  globalShortcut.unregisterAll()

  const registered = globalShortcut.register(hotkey, () => {
    toggleRecording()
  })

  if (!registered) {
    dialog.showErrorBox('Hotkey Error', `Failed to register hotkey: ${hotkey}`)
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

ipcMain.handle('export-transcript', async (_, { text, format, speakers }: any) => {
  const result = await dialog.showSaveDialog(mainWindow!, {
    defaultPath: `transcript-${Date.now()}.${format}`,
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'SRT Subtitles', extensions: ['srt'] },
      { name: 'WebVTT', extensions: ['vtt'] },
      { name: 'JSON', extensions: ['json'] },
      { name: 'CSV', extensions: ['csv'] },
    ],
  })

  if (!result.canceled && result.filePath) {
    let content = text

    if (format === 'json') {
      content = JSON.stringify({ text, speakers, timestamp: new Date().toISOString() }, null, 2)
    } else if (format === 'csv' && speakers) {
      content = 'Speaker,Start,End,Text\n' +
        speakers.map((s: any) => `"${s.speaker}",${s.start},${s.end},"${s.text}"`).join('\n')
    } else if (format === 'srt' && speakers) {
      content = speakers.map((s: any, i: number) => {
        const start = formatTime(s.start)
        const end = formatTime(s.end)
        return `${i + 1}\n${start} --> ${end}\n${s.speaker}: ${s.text}\n`
      }).join('\n')
    } else if (format === 'vtt' && speakers) {
      content = 'WEBVTT\n\n' +
        speakers.map((s: any) => {
          const start = formatTime(s.start)
          const end = formatTime(s.end)
          return `${start} --> ${end}\n${s.speaker}: ${s.text}\n`
        }).join('\n')
    }

    fs.writeFileSync(result.filePath, content)
    return true
  }
  return false
})

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 1000)
  return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(3, '0')}`
}

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
