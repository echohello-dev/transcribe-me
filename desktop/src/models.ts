export interface ModelInfo {
  id: string
  name: string
  engine: 'parakeet' | 'whisperkit' | 'whispercpp' | 'openai' | 'assemblyai' | 'apple'
  size: string
  sizeBytes: number
  description: string
  features: string[]
  isLocal: boolean
  isDownloaded: boolean
  isActive: boolean
  hfRepo?: string
  language?: string
  isPro?: boolean
  category: string
  icon: string
  iconColor: string
}

export interface CloudProvider {
  id: string
  name: string
  description: string
  requiresKey: boolean
  models: ModelInfo[]
}

export const LOCAL_MODELS: ModelInfo[] = [
  {
    id: 'parakeet-tdt-0.6b-v3',
    name: 'Parakeet TDT 0.6B v3',
    engine: 'parakeet',
    size: '600 MB',
    sizeBytes: 600 * 1024 * 1024,
    description: 'Best balance of speed and accuracy',
    features: ['Fast', 'Accurate'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    hfRepo: 'mlx-community/parakeet-tdt-0.6b-v3',
    category: 'Recommended',
    icon: '🦜',
    iconColor: '#7cb342',
  },
  {
    id: 'parakeet-tdt-1.1b',
    name: 'Parakeet TDT 1.1B',
    engine: 'parakeet',
    size: '1.1 GB',
    sizeBytes: 1.1 * 1024 * 1024 * 1024,
    description: 'Higher accuracy with larger context',
    features: ['High Accuracy', 'Larger Context'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    hfRepo: 'mlx-community/parakeet-tdt-1.1b',
    category: 'Recommended',
    icon: '🦜',
    iconColor: '#7cb342',
  },
  {
    id: 'parakeet-tdt-0.6b-v3-speaker',
    name: 'Parakeet v3',
    engine: 'parakeet',
    size: '1.24 GB',
    sizeBytes: 1.24 * 1024 * 1024 * 1024,
    description: 'Speaker Recognition',
    features: ['Speaker Recognition', 'High Accuracy'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    hfRepo: 'mlx-community/parakeet-tdt-0.6b-v3',
    category: 'Speaker Recognition',
    icon: '🦜',
    iconColor: '#7cb342',
  },
  {
    id: 'parakeet-tdt-0.6b-v3-small',
    name: 'Parakeet v3 (494MB)',
    engine: 'parakeet',
    size: '494 MB',
    sizeBytes: 494 * 1024 * 1024,
    description: 'Speaker Recognition - Smaller variant',
    features: ['Speaker Recognition', 'Compact'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    hfRepo: 'mlx-community/parakeet-tdt-0.6b-v3',
    category: 'Speaker Recognition',
    icon: '🦜',
    iconColor: '#7cb342',
  },
  {
    id: 'whisperkit-small',
    name: 'Small',
    engine: 'whisperkit',
    size: '483 MB',
    sizeBytes: 483 * 1024 * 1024,
    description: 'WhisperKit, Speaker Recognition',
    features: ['Speaker Recognition', 'Fast'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    category: 'Recommended',
    icon: '🔮',
    iconColor: '#5c6bc0',
  },
  {
    id: 'whisperkit-large-v2',
    name: 'Large v2',
    engine: 'whisperkit',
    size: '3.1 GB',
    sizeBytes: 3.1 * 1024 * 1024 * 1024,
    description: 'WhisperKit, Speaker Recognition',
    features: ['Speaker Recognition', 'Best Accuracy'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    category: 'Pro',
    icon: '🔮',
    iconColor: '#5c6bc0',
    isPro: true,
  },
  {
    id: 'whispercpp-tiny',
    name: 'Tiny',
    engine: 'whispercpp',
    size: '75 MB',
    sizeBytes: 75 * 1024 * 1024,
    description: 'Fastest, smallest model',
    features: ['Super Fast', 'Low Memory'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    category: 'Basic',
    icon: '⚡',
    iconColor: '#ffa726',
  },
  {
    id: 'whispercpp-base',
    name: 'Base',
    engine: 'whispercpp',
    size: '150 MB',
    sizeBytes: 150 * 1024 * 1024,
    description: 'Good balance for clear audio',
    features: ['Fast', 'Accurate'],
    isLocal: true,
    isDownloaded: false,
    isActive: false,
    category: 'Basic',
    icon: '⚡',
    iconColor: '#ffa726',
  },
  {
    id: 'apple-speech-en',
    name: 'Apple Speech (English)',
    engine: 'apple',
    size: 'Built-in',
    sizeBytes: 0,
    description: 'On-device Apple Speech recognition',
    features: ['Offline', 'Fast'],
    isLocal: true,
    isDownloaded: true,
    isActive: false,
    language: 'en',
    category: 'Apple Speech',
    icon: '🍎',
    iconColor: '#ef5350',
  },
]

export const CLOUD_PROVIDERS: CloudProvider[] = [
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'Whisper API - Highly accurate cloud transcription',
    requiresKey: true,
    models: [
      {
        id: 'openai-whisper-1',
        name: 'Whisper-1',
        engine: 'openai',
        size: 'Cloud',
        sizeBytes: 0,
        description: 'OpenAI Whisper API',
        features: ['Cloud', '99 Languages'],
        isLocal: false,
        isDownloaded: true,
        isActive: false,
        category: 'Cloud',
        icon: '☁️',
        iconColor: '#10a37f',
      },
    ],
  },
  {
    id: 'assemblyai',
    name: 'AssemblyAI',
    description: 'Advanced features including speaker diarization',
    requiresKey: true,
    models: [
      {
        id: 'assemblyai-best',
        name: 'Universal',
        engine: 'assemblyai',
        size: 'Cloud',
        sizeBytes: 0,
        description: 'Best accuracy with speaker labels',
        features: ['Speaker Diarization', 'Sentiment', 'Topics'],
        isLocal: false,
        isDownloaded: true,
        isActive: false,
        category: 'Cloud',
        icon: '☁️',
        iconColor: '#2563eb',
      },
    ],
  },
]

export const MODEL_CATEGORIES = [
  { id: 'apple', name: 'Apple Speech', icon: '🍎', description: 'On-device Apple Speech recognition' },
  { id: 'language', name: 'Language Specific', icon: '🌐', description: 'Models that can only transcribe in one language' },
  { id: 'whisperkit', name: 'WhisperKit', icon: '🔮', description: 'Models that use the WhisperKit engine for greater accuracy' },
  { id: 'parakeet', name: 'Parakeet', icon: '🦜', description: 'Models that use the Nvidia Parakeet engine' },
  { id: 'whispercpp', name: 'Whisper C++', icon: '⚡', description: 'Models that use the Whisper C++ engine' },
  { id: 'pro', name: 'Pro', icon: '⭐', description: 'Models available exclusively to Pro users' },
  { id: 'speaker', name: 'Speaker Recognition', icon: '👥', description: 'Models that can identify and separate different speakers' },
  { id: 'advanced', name: 'Advanced', icon: '🔬', description: 'Models for advanced users' },
]

export const EXPORT_FORMATS = [
  { id: 'txt', name: 'Plain Text', extension: '.txt', description: 'Simple text file' },
  { id: 'srt', name: 'SRT Subtitles', extension: '.srt', description: 'Subtitle format with timestamps' },
  { id: 'vtt', name: 'WebVTT', extension: '.vtt', description: 'Web video text tracks' },
  { id: 'json', name: 'JSON', extension: '.json', description: 'Structured data format' },
  { id: 'csv', name: 'CSV', extension: '.csv', description: 'Spreadsheet format' },
  { id: 'pdf', name: 'PDF', extension: '.pdf', description: 'Portable document format' },
  { id: 'docx', name: 'Word Document', extension: '.docx', description: 'Microsoft Word format' },
]
