import { useState, useEffect, useCallback } from 'react'
import {
  Mic, Settings, Download, Keyboard, Monitor, FileText,
  Activity, Copy, Check, Star, Users, Globe, Zap,
  Apple, FlaskConical, ChevronRight, X, Cloud, HardDrive
} from 'lucide-react'
import {
  LOCAL_MODELS, CLOUD_PROVIDERS, MODEL_CATEGORIES, EXPORT_FORMATS,
  type ModelInfo, type CloudProvider
} from './models'
import './App.css'

type View = 'home' | 'settings' | 'models' | 'history'
type ModelTab = 'local' | 'cloud'

interface TranscriptionRecord {
  id: string
  text: string
  timestamp: Date
  speakers?: SpeakerSegment[]
  duration?: number
}

interface SpeakerSegment {
  speaker: string
  text: string
  start: number
  end: number
}

function App() {
  const [currentView, setCurrentView] = useState<View>('home')
  const [modelTab, setModelTab] = useState<ModelTab>('local')
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [speakers, setSpeakers] = useState<SpeakerSegment[]>([])
  const [history, setHistory] = useState<TranscriptionRecord[]>([])
  const [hotkey, setHotkey] = useState('Cmd+Shift+Space')
  const [detectedApps, setDetectedApps] = useState<string[]>([])
  const [meetingDetection, setMeetingDetection] = useState(true)
  const [autoPaste, setAutoPaste] = useState(true)
  const [showOverlay, setShowOverlay] = useState(false)
  const [models, setModels] = useState<ModelInfo[]>(LOCAL_MODELS)
  const [cloudProviders] = useState<CloudProvider[]>(CLOUD_PROVIDERS)
  const [activeModelId, setActiveModelId] = useState<string>('')
  const [downloadingModel, setDownloadingModel] = useState<string | null>(null)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [copiedToClipboard, setCopiedToClipboard] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [cloudProvider, setCloudProvider] = useState('')
  const [openaiKey, setOpenaiKey] = useState('')
  const [assemblyaiKey, setAssemblyaiKey] = useState('')

  const electronAPI = (window as any).electronAPI

  useEffect(() => {
    const loadSettings = async () => {
      const savedHotkey = await electronAPI.getStoreValue('hotkey')
      const savedAutoPaste = await electronAPI.getStoreValue('autoPaste')
      const savedMeetingDetection = await electronAPI.getStoreValue('meetingDetection')
      const savedModelId = await electronAPI.getStoreValue('activeModelId')
      const savedModels = await electronAPI.getStoreValue('models')
      const savedCloudProvider = await electronAPI.getStoreValue('cloudProvider')
      const savedOpenaiKey = await electronAPI.getStoreValue('openaiApiKey')
      const savedAssemblyaiKey = await electronAPI.getStoreValue('assemblyaiApiKey')

      if (savedHotkey) setHotkey(savedHotkey)
      if (savedAutoPaste !== undefined) setAutoPaste(savedAutoPaste)
      if (savedMeetingDetection !== undefined) setMeetingDetection(savedMeetingDetection)
      if (savedModelId) setActiveModelId(savedModelId)
      if (savedModels) setModels(savedModels)
      if (savedCloudProvider) setCloudProvider(savedCloudProvider)
      if (savedOpenaiKey) setOpenaiKey(savedOpenaiKey)
      if (savedAssemblyaiKey) setAssemblyaiKey(savedAssemblyaiKey)
    }
    loadSettings()

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

    electronAPI.onTranscriptionResult((result: any) => {
      setIsTranscribing(false)
      setShowOverlay(false)

      if (typeof result === 'object' && result.text) {
        setTranscript(result.text)
        if (result.speakers) setSpeakers(result.speakers)
      } else {
        setTranscript(result)
      }

      const record: TranscriptionRecord = {
        id: Date.now().toString(),
        text: typeof result === 'object' ? result.text : result,
        timestamp: new Date(),
        speakers: typeof result === 'object' ? result.speakers : undefined,
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
    await electronAPI.setStoreValue('activeModelId', activeModelId)
    await electronAPI.setStoreValue('models', models)
    await electronAPI.setStoreValue('cloudProvider', cloudProvider)
    await electronAPI.setStoreValue('openaiApiKey', openaiKey)
    await electronAPI.setStoreValue('assemblyaiApiKey', assemblyaiKey)
  }

  const activateModel = (modelId: string) => {
    setActiveModelId(modelId)
    setModels(prev => prev.map(m => ({
      ...m,
      isActive: m.id === modelId
    })))
  }

  const downloadModel = async (model: ModelInfo) => {
    if (!model.hfRepo) return
    setDownloadingModel(model.id)
    try {
      await electronAPI.downloadModel(model.hfRepo)
      setModels(prev => prev.map(m =>
        m.id === model.id ? { ...m, isDownloaded: true } : m
      ))
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setDownloadingModel(null)
    }
  }

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(transcript)
    setCopiedToClipboard(true)
    setTimeout(() => setCopiedToClipboard(false), 2000)
  }

  const exportTranscript = async (formatId: string) => {
    const format = EXPORT_FORMATS.find(f => f.id === formatId)
    if (!format) return

    await electronAPI.exportTranscript({
      text: transcript,
      format: formatId,
      speakers,
    })
    setShowExportDialog(false)
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
          <div className="transcript-header">
            <h3>Transcription</h3>
            <div className="transcript-actions">
              <button onClick={copyToClipboard} className="icon-button">
                {copiedToClipboard ? <Check size={16} /> : <Copy size={16} />}
                {copiedToClipboard ? 'Copied!' : 'Copy'}
              </button>
              <button onClick={() => setShowExportDialog(true)} className="icon-button">
                <Download size={16} />
                Export
              </button>
            </div>
          </div>

          {speakers.length > 0 ? (
            <div className="speaker-transcript">
              {speakers.map((seg, i) => (
                <div key={i} className="speaker-segment">
                  <span className="speaker-label">{seg.speaker}</span>
                  <p>{seg.text}</p>
                </div>
              ))}
            </div>
          ) : (
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              rows={8}
            />
          )}
        </div>
      )}
    </div>
  )

  const renderModels = () => (
    <div className="models-view">
      <div className="models-header">
        <h2>Models</h2>
        <div className="model-tabs">
          <button
            className={modelTab === 'local' ? 'active' : ''}
            onClick={() => setModelTab('local')}
          >
            <HardDrive size={16} />
            Local
          </button>
          <button
            className={modelTab === 'cloud' ? 'active' : ''}
            onClick={() => setModelTab('cloud')}
          >
            <Cloud size={16} />
            Cloud
          </button>
        </div>
      </div>

      {modelTab === 'local' ? (
        <>
          {models.some(m => m.isDownloaded) && (
            <div className="model-section">
              <h3>Downloaded</h3>
              <div className="model-list">
                {models.filter(m => m.isDownloaded).map(model => (
                  <ModelCard
                    key={model.id}
                    model={model}
                    isActive={model.id === activeModelId}
                    isDownloading={downloadingModel === model.id}
                    onActivate={() => activateModel(model.id)}
                    onDownload={() => downloadModel(model)}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="model-section">
            <h3>Categories</h3>
            <div className="category-list">
              {MODEL_CATEGORIES.map(cat => (
                <button
                  key={cat.id}
                  className={`category-card ${selectedCategory === cat.id ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(selectedCategory === cat.id ? null : cat.id)}
                >
                  <div className="category-icon">{cat.icon}</div>
                  <div className="category-info">
                    <h4>{cat.name}</h4>
                    <p>{cat.description}</p>
                  </div>
                  <ChevronRight size={18} />
                </button>
              ))}
            </div>
          </div>

          <div className="model-section">
            <h3>Recommended Models</h3>
            <div className="model-list">
              {models
                .filter(m => !selectedCategory || m.category.toLowerCase().includes(selectedCategory))
                .map(model => (
                  <ModelCard
                    key={model.id}
                    model={model}
                    isActive={model.id === activeModelId}
                    isDownloading={downloadingModel === model.id}
                    onActivate={() => activateModel(model.id)}
                    onDownload={() => downloadModel(model)}
                  />
                ))}
            </div>
          </div>
        </>
      ) : (
        <div className="cloud-providers">
          {cloudProviders.map(provider => (
            <div key={provider.id} className="provider-card">
              <div className="provider-header">
                <Cloud size={24} />
                <div>
                  <h3>{provider.name}</h3>
                  <p>{provider.description}</p>
                </div>
              </div>
              <div className="provider-models">
                {provider.models.map(model => (
                  <ModelCard
                    key={model.id}
                    model={model}
                    isActive={model.id === activeModelId}
                    isDownloading={false}
                    onActivate={() => activateModel(model.id)}
                    onDownload={() => {}}
                  />
                ))}
              </div>
            </div>
          ))}
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
        <h3>Cloud Providers</h3>
        <div className="setting-item">
          <label>
            <Cloud size={16} />
            Active Provider
          </label>
          <select
            value={cloudProvider}
            onChange={(e) => setCloudProvider(e.target.value)}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              padding: '8px 12px',
              color: 'var(--text-primary)',
              fontSize: '14px',
            }}
          >
            <option value="">None (Local Only)</option>
            <option value="openai">OpenAI</option>
            <option value="assemblyai">AssemblyAI</option>
          </select>
        </div>

        {cloudProvider === 'openai' && (
          <div className="setting-item">
            <label>OpenAI API Key</label>
            <input
              type="password"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              placeholder="sk-..."
            />
          </div>
        )}

        {cloudProvider === 'assemblyai' && (
          <div className="setting-item">
            <label>AssemblyAI API Key</label>
            <input
              type="password"
              value={assemblyaiKey}
              onChange={(e) => setAssemblyaiKey(e.target.value)}
              placeholder="..."
            />
          </div>
        )}
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
                <div className="history-actions">
                  <button onClick={() => navigator.clipboard.writeText(record.text)}>
                    <Copy size={14} />
                  </button>
                </div>
              </div>
              {record.speakers ? (
                <div className="speaker-preview">
                  {record.speakers.slice(0, 3).map((seg, i) => (
                    <p key={i}><strong>{seg.speaker}:</strong> {seg.text}</p>
                  ))}
                </div>
              ) : (
                <p>{record.text.substring(0, 200)}...</p>
              )}
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

      {showExportDialog && (
        <div className="export-dialog-overlay" onClick={() => setShowExportDialog(false)}>
          <div className="export-dialog" onClick={e => e.stopPropagation()}>
            <div className="export-dialog-header">
              <h3>Export Transcription</h3>
              <button onClick={() => setShowExportDialog(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="export-formats">
              {EXPORT_FORMATS.map(format => (
                <button
                  key={format.id}
                  className="export-format-button"
                  onClick={() => exportTranscript(format.id)}
                >
                  <FileText size={20} />
                  <div>
                    <span className="format-name">{format.name}</span>
                    <span className="format-desc">{format.description}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
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

interface ModelCardProps {
  model: ModelInfo
  isActive: boolean
  isDownloading: boolean
  onActivate: () => void
  onDownload: () => void
}

function ModelCard({ model, isActive, isDownloading, onActivate, onDownload }: ModelCardProps) {
  return (
    <div className={`model-card ${isActive ? 'active' : ''}`}>
      <div className="model-icon" style={{ backgroundColor: model.iconColor + '20', color: model.iconColor }}>
        {model.icon}
      </div>
      <div className="model-info">
        <div className="model-name-row">
          <h4>{model.name}</h4>
          <div className="model-badges">
            {model.features.includes('Speaker Recognition') && (
              <span className="badge speaker" title="Speaker Recognition">
                <Users size={12} />
              </span>
            )}
            {model.isPro && (
              <span className="badge pro" title="Pro">
                <Star size={12} />
              </span>
            )}
            {model.language && (
              <span className="badge language">{model.language}</span>
            )}
          </div>
        </div>
        <p className="model-description">{model.description} - {model.size}</p>
      </div>
      <div className="model-actions">
        {model.isDownloaded || !model.isLocal ? (
          isActive ? (
            <span className="active-label">Active</span>
          ) : (
            <button className="activate-button" onClick={onActivate}>
              Activate
            </button>
          )
        ) : (
          <button
            className="download-button"
            onClick={onDownload}
            disabled={isDownloading}
          >
            {isDownloading ? 'Downloading...' : 'Download'}
          </button>
        )}
      </div>
    </div>
  )
}

export default App
