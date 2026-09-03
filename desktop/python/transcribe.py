#!/usr/bin/env python3
"""
Transcription backend using parakeet-mlx for local on-device transcription.
"""

import argparse
import sys
import os
import json
from pathlib import Path

def transcribe_with_parakeet(audio_path: str, model_id: str = "mlx-community/parakeet-tdt-0.6b-v3", language: str = "en") -> str:
    """Transcribe audio using parakeet-mlx."""
    try:
        from parakeet_mlx import from_pretrained
        
        # Load model (downloads on first use)
        model = from_pretrained(model_id)
        
        # Transcribe
        result = model.transcribe(audio_path)
        return result.text
    except ImportError:
        print("Error: parakeet-mlx not installed. Run: pip install parakeet-mlx", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Transcription error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Transcribe audio file")
    parser.add_argument("audio_path", help="Path to audio file")
    parser.add_argument("--model", default="mlx-community/parakeet-tdt-0.6b-v3", help="Model ID")
    parser.add_argument("--language", default="en", help="Language code")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_path):
        print(f"Error: Audio file not found: {args.audio_path}", file=sys.stderr)
        sys.exit(1)
    
    transcript = transcribe_with_parakeet(args.audio_path, args.model, args.language)
    print(transcript)

if __name__ == "__main__":
    main()
