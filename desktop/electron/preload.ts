import { contextBridge, ipcRenderer } from 'electron'

export interface ElectronAPI {
  getStoreValue: (key: string) => Promise<any>
  setStoreValue: (key: string, value: any) => Promise<void>
  toggleRecording: () => Promise<void>
  getRecordingStatus: () => Promise<boolean>
  selectModelPath: () => Promise<string | null>
  downloadModel: (modelId: string) => Promise<string>
  detectMeetingApps: () => Promise<string[]>
  exportTranscript: (data: any) => Promise<boolean>
  onRecordingStarted: (callback: () => void) => void
  onRecordingStopped: (callback: () => void) => void
  onRecordingError: (callback: (error: string) => void) => void
  onTranscriptionStarted: (callback: () => void) => void
  onTranscriptionResult: (callback: (result: any) => void) => void
  onTranscriptionError: (callback: (error: string) => void) => void
  onDownloadProgress: (callback: (progress: string) => void) => void
  onMeetingAppsDetected: (callback: (apps: string[]) => void) => void
  onNavigateToSettings: (callback: () => void) => void
  removeAllListeners: (channel: string) => void
}

const api: ElectronAPI = {
  getStoreValue: (key: string) => ipcRenderer.invoke('get-store-value', key),
  setStoreValue: (key: string, value: any) => ipcRenderer.invoke('set-store-value', key, value),
  toggleRecording: () => ipcRenderer.invoke('toggle-recording'),
  getRecordingStatus: () => ipcRenderer.invoke('get-recording-status'),
  selectModelPath: () => ipcRenderer.invoke('select-model-path'),
  downloadModel: (modelId: string) => ipcRenderer.invoke('download-model', modelId),
  detectMeetingApps: () => ipcRenderer.invoke('detect-meeting-apps'),
  exportTranscript: (data: any) => ipcRenderer.invoke('export-transcript', data),

  onRecordingStarted: (callback: () => void) => {
    ipcRenderer.on('recording-started', () => callback())
  },
  onRecordingStopped: (callback: () => void) => {
    ipcRenderer.on('recording-stopped', () => callback())
  },
  onRecordingError: (callback: (error: string) => void) => {
    ipcRenderer.on('recording-error', (_, error) => callback(error))
  },
  onTranscriptionStarted: (callback: () => void) => {
    ipcRenderer.on('transcription-started', () => callback())
  },
  onTranscriptionResult: (callback: (result: any) => void) => {
    ipcRenderer.on('transcription-result', (_, result) => callback(result))
  },
  onTranscriptionError: (callback: (error: string) => void) => {
    ipcRenderer.on('transcription-error', (_, error) => callback(error))
  },
  onDownloadProgress: (callback: (progress: string) => void) => {
    ipcRenderer.on('download-progress', (_, progress) => callback(progress))
  },
  onMeetingAppsDetected: (callback: (apps: string[]) => void) => {
    ipcRenderer.on('meeting-apps-detected', (_, apps) => callback(apps))
  },
  onNavigateToSettings: (callback: () => void) => {
    ipcRenderer.on('navigate-to-settings', () => callback())
  },
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel)
  },
}

contextBridge.exposeInMainWorld('electronAPI', api)

export type { ElectronAPI }
