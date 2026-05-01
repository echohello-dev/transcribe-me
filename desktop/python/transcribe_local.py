#!/usr/bin/env python3
"""
Transcribe using a locally downloaded model.
"""

import argparse
import sys
import os

def transcribe_with_local_model(audio_path: str, model_path: str, language: str = "en") -> str:
    """Transcribe audio using a local model path."""
    try:
        from parakeet_mlx import from_pretrained
        
        # Load model from local path
        model = from_pretrained(model_path)
        
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
    parser = argparse.ArgumentParser(description="Transcribe audio file with local model")
    parser.add_argument("audio_path", help="Path to audio file")
    parser.add_argument("--model", required=True, help="Path to local model directory")
    parser.add_argument("--language", default="en", help="Language code")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_path):
        print(f"Error: Audio file not found: {args.audio_path}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.model):
        print(f"Error: Model directory not found: {args.model}", file=sys.stderr)
        sys.exit(1)
    
    transcript = transcribe_with_local_model(args.audio_path, args.model, args.language)
    print(transcript)

if __name__ == "__main__":
    main()
