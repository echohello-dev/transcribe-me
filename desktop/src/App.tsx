import { useState, useEffect, useCallback } from 'react'
import { Mic, Settings, Download, Keyboard, Monitor, FileText, Activity } from 'lucide-react'
import './App.css'

type View = 'home' | 'settings' | 'models' | 'history'

interface TranscriptionRecord {
  id: string
  text: string
  timestamp: Date
  duration?: number
}

function App() {
  const [currentView, setCurrentView] = useState<View>('home')
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [history, setHistory] = useState<TranscriptionRecord[]>([])
  const [hotkey, setHotkey] = useState('Cmd+Shift+Space')
  const [detectedApps, setDetectedApps] = useState<string[]>([])
  const [meetingDetection, setMeetingDetection] = useState(true)
  const [autoPaste, setAutoPaste] = useState(true)
  const [showOverlay, setShowOverlay] = useState(false)

  const electronAPI = (window as any).electronAPI

  useEffect(() => {
    // Load settings
    const loadSettings = async () => {
      const savedHotkey = await electronAPI.getStoreValue('hotkey')
      const savedAutoPaste = await electronAPI.getStoreValue('autoPaste')
      const savedMeetingDetection = await electronAPI.getStoreValue('meetingDetection')
      
      if (savedHotkey) setHotkey(savedHotkey)
      if (savedAutoPaste !== undefined) setAutoPaste(savedAutoPaste)
      if (savedMeetingDetection !== undefined) setMeetingDetection(savedMeetingDetection)
    }
    loadSettings()

    // Set up event listeners
    electronAPI.onRecordingStarted(() => {
      setIsRecording(true)
      setShowOverlay(true)
    })

    electronAPI.onRecordingStopped(() => {
      setIsRecording(false)
      setIsTranscribing(true)
    })

    electronAPI.onRecordingError((error: string) => {
      setIsRecording(false)
      setIsTranscribing(false)
      console.error('Recording error:', error)
    })

    electronAPI.onTranscriptionStarted(() => {
      setIsTranscribing(true)
    })

    electronAPI.onTranscriptionResult((text: string) => {
      setIsTranscribing(false)
      setShowOverlay(false)
      setTranscript(text)
      
      const record: TranscriptionRecord = {
        id: Date.now().toString(),
        text,
        timestamp: new Date(),
      }
      setHistory(prev => [record, ...prev])
    })

    electronAPI.onTranscriptionError((error: string) => {
      setIsTranscribing(false)
      setShowOverlay(false)
      console.error('Transcription error:', error)
    })

    electronAPI.onMeetingAppsDetected((apps: string[]) => {
      setDetectedApps(apps)
    })

    electronAPI.onNavigateToSettings(() => {
      setCurrentView('settings')
    })

    // Detect meeting apps periodically
    const detectInterval = setInterval(() => {
      if (meetingDetection) {
        electronAPI.detectMeetingApps()
      }
    }, 5000)

    return () => {
      clearInterval(detectInterval)
      electronAPI.removeAllListeners('recording-started')
      electronAPI.removeAllListeners('recording-stopped')
      electronAPI.removeAllListeners('recording-error')
      electronAPI.removeAllListeners('transcription-started')
      electronAPI.removeAllListeners('transcription-result')
      electronAPI.removeAllListeners('transcription-error')
      electronAPI.removeAllListeners('meeting-apps-detected')
      electronAPI.removeAllListeners('navigate-to-settings')
    }
  }, [meetingDetection])

  const toggleRecording = useCallback(async () => {
    await electronAPI.toggleRecording()
  }, [])

  const saveSettings = async () => {
    await electronAPI.setStoreValue('hotkey', hotkey)
    await electronAPI.setStoreValue('autoPaste', autoPaste)
    await electronAPI.setStoreValue('meetingDetection', meetingDetection)
  }

  const renderHome = () => (
    <div className="home-view">
      <div className="recording-section">
        <button
          className={`record-button ${isRecording ? 'recording' : ''} ${isTranscribing ? 'transcribing' : ''}`}
          onClick={toggleRecording}
        >
          <Mic size={48} />
          <span>{isRecording ? 'Stop' : isTranscribing ? 'Transcribing...' : 'Record'}</span>
        </button>
        
        <div className="hotkey-hint">
          Press <kbd>{hotkey}</kbd> to {isRecording ? 'stop' : 'start'}
        </div>
      </div>

      {detectedApps.length > 0 && (
        <div className="detected-apps">
          <Monitor size={16} />
          <span>Detected: {detectedApps.join(', ')}</span>
        </div>
      )}

      {transcript && (
        <div className="transcript-result">
          <h3>Transcription</h3>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            rows={8}
          />
          <div className="transcript-actions">
            <button onClick={() => navigator.clipboard.writeText(transcript)}>
              Copy to Clipboard
            </button>
          </div>
        </div>
      )}
    </div>
  )

  const renderSettings = () => (
    <div className="settings-view">
      <h2>Settings</h2>
      
      <div className="setting-group">
        <h3>Recording</h3>
        <div className="setting-item">
          <label>
            <Keyboard size={16} />
            Hotkey
          </label>
          <input
            type="text"
            value={hotkey}
            onChange={(e) => setHotkey(e.target.value)}
            placeholder="e.g., Cmd+Shift+Space"
          />
        </div>
        
        <div className="setting-item">
          <label>
            <FileText size={16} />
            Auto-paste
          </label>
          <input
            type="checkbox"
            checked={autoPaste}
            onChange={(e) => setAutoPaste(e.target.checked)}
          />
        </div>
      </div>

      <div className="setting-group">
        <h3>Detection</h3>
        <div className="setting-item">
          <label>
            <Monitor size={16} />
            Meeting App Detection
          </label>
          <input
            type="checkbox"
            checked={meetingDetection}
            onChange={(e) => setMeetingDetection(e.target.checked)}
          />
        </div>
      </div>

      <button className="save-button" onClick={saveSettings}>
        Save Settings
      </button>
    </div>
  )

  const renderModels = () => (
    <div className="models-view">
      <h2>Models</h2>
      <div className="model-list">
        <div className="model-card">
          <div className="model-info">
            <h3>Parakeet TDT 0.6B v3</h3>
            <p>Best balance of speed and accuracy</p>
            <span className="model-size">~600MB</span>
          </div>
          <button className="download-button">
            <Download size={16} />
            Install
          </button>
        </div>
        
        <div className="model-card">
          <div className="model-info">
            <h3>Parakeet TDT 1.1B</h3>
            <p>Higher accuracy, larger model</p>
            <span className="model-size">~1.1GB</span>
          </div>
          <button className="download-button">
            <Download size={16} />
            Install
          </button>
        </div>
        
        <div className="model-card">
          <div className="model-info">
            <h3>Parakeet RNNT 0.6B</h3>
            <p>Streaming optimized</p>
            <span className="model-size">~600MB</span>
          </div>
          <button className="download-button">
            <Download size={16} />
            Install
          </button>
        </div>
      </div>
    </div>
  )

  const renderHistory = () => (
    <div className="history-view">
      <h2>History</h2>
      {history.length === 0 ? (
        <div className="empty-state">
          <Activity size={48} />
          <p>No transcriptions yet</p>
        </div>
      ) : (
        <div className="history-list">
          {history.map((record) => (
            <div key={record.id} className="history-item">
              <div className="history-meta">
                <span>{record.timestamp.toLocaleString()}</span>
              </div>
              <p>{record.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div className="app">
      {showOverlay && (
        <div className="recording-overlay">
          <div className="waveform">
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
            <div className="bar" />
          </div>
          <p>{isRecording ? 'Recording...' : 'Transcribing...'}</p>
        </div>
      )}

      <aside className="sidebar">
        <div className="logo">
          <Mic size={24} />
          <span>Transcribe</span>
        </div>
        
        <nav>
          <button
            className={currentView === 'home' ? 'active' : ''}
            onClick={() => setCurrentView('home')}
          >
            <Mic size={18} />
            Record
          </button>
          <button
            className={currentView === 'history' ? 'active' : ''}
            onClick={() => setCurrentView('history')}
          >
            <FileText size={18} />
            History
          </button>
          <button
            className={currentView === 'models' ? 'active' : ''}
            onClick={() => setCurrentView('models')}
          >
            <Download size={18} />
            Models
          </button>
          <button
            className={currentView === 'settings' ? 'active' : ''}
            onClick={() => setCurrentView('settings')}
          >
            <Settings size={18} />
            Settings
          </button>
        </nav>
      </aside>

      <main className="content">
        {currentView === 'home' && renderHome()}
        {currentView === 'settings' && renderSettings()}
        {currentView === 'models' && renderModels()}
        {currentView === 'history' && renderHistory()}
      </main>
    </div>
  )
}

export default App
