# Transcribe Me Desktop

A desktop transcription application built with Electron, React, and TypeScript. Features local on-device transcription using MLX Parakeet models, global hotkeys, meeting app detection, and system-wide voice-to-text.

## Features

- **Local Transcription**: Uses MLX Parakeet models for on-device transcription — no audio leaves your machine
- **Global Hotkeys**: Start/stop recording from anywhere with customizable keyboard shortcuts
- **Meeting App Detection**: Automatically detects when Zoom, Teams, Webex, Skype, Discord, or Chime are running
- **System Tray Integration**: Runs in the background with menu bar access
- **Auto-Paste**: Automatically inserts transcribed text into the active application
- **Model Management**: Download and manage different Parakeet model variants
- **History**: Keep a log of all your transcriptions

## Architecture

```
desktop/
├── electron/
│   ├── main.ts          # Main Electron process (window, tray, hotkeys, IPC)
│   └── preload.ts       # Preload script for secure IPC bridge
├── python/
│   ├── transcribe.py    # Parakeet MLX transcription backend
│   ├── transcribe_local.py  # Local model transcription
│   └── download_model.py    # Model download utility
├── src/
│   ├── App.tsx          # Main React application
│   ├── App.css          # Styles
│   ├── main.tsx         # React entry point
│   └── index.css        # Global styles
├── package.json         # Dependencies and build config
└── vite.config.ts       # Vite + Electron build configuration
```

## Prerequisites

- **macOS**: macOS 14+ with Apple Silicon (M1/M2/M3) for MLX support
- **Python**: Python 3.9+ with `parakeet-mlx` installed
- **Node.js**: Node.js 18+ and npm
- **sox/rec**: For audio recording (`brew install sox`)

## Installation

### 1. Install Python Dependencies

```bash
pip install parakeet-mlx
```

### 2. Install Node Dependencies

```bash
cd desktop
npm install
```

### 3. Run in Development Mode

```bash
npm run dev
```

### 4. Build for Production

```bash
# macOS
npm run build:mac

# Windows
npm run build:win
```

## Usage

### Recording

1. Press the global hotkey (default: `Cmd+Shift+Space`) or click the Record button
2. Speak into your microphone
3. Press the hotkey again or click Stop
4. The transcription will appear and be copied to your clipboard

### Model Installation

1. Go to the **Models** tab
2. Click **Install** on the desired model
3. The model will download from Hugging Face (~600MB-1.1GB)

### Settings

- **Hotkey**: Change the global shortcut (e.g., `Cmd+Shift+Space`, `Ctrl+Alt+R`)
- **Auto-paste**: Automatically insert text into the active app
- **Meeting Detection**: Detect running meeting applications

## Available Models

| Model | Size | Type | Best For |
|-------|------|------|----------|
| Parakeet TDT 0.6B v3 | ~600MB | TDT | General use, best accuracy |
| Parakeet TDT 1.1B | ~1.1GB | TDT | Higher accuracy |
| Parakeet RNNT 0.6B | ~600MB | RNNT | Streaming |
| Parakeet CTC 0.6B | ~600MB | CTC | Fast real-time |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+Space` (default) | Start/stop recording |
| `Esc` | Cancel recording |

## Privacy

All transcription happens locally on your device. No audio data is sent to external servers. The application uses:
- **MLX Parakeet models** running on Apple Silicon
- **Local audio processing** via sox/rec
- **No cloud dependencies** for transcription

## Development

### Project Structure

- **Electron Main Process**: Handles window management, global shortcuts, system tray, and IPC communication
- **Electron Preload**: Secure bridge between main and renderer processes
- **React Frontend**: UI components for recording, settings, models, and history
- **Python Backend**: MLX Parakeet transcription engine

### Tech Stack

- **Frontend**: React 19, TypeScript, Vite
- **Desktop**: Electron 41
- **Styling**: CSS with CSS variables for theming
- **Audio**: sox/rec for recording, WAV format
- **ML**: parakeet-mlx (Python) for transcription
- **Icons**: Lucide React

### Building

The project uses `vite-plugin-electron` for development and `electron-builder` for packaging:

```bash
# Development (hot reload for both main and renderer)
npm run dev

# Production build
npm run build

# Platform-specific builds
npm run build:mac    # macOS DMG
npm run build:win    # Windows NSIS installer
```

## License

MIT
