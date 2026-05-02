#!/usr/bin/env python3
"""
Cloud transcription backend supporting OpenAI and AssemblyAI.
"""

import argparse
import sys
import os
import json

def transcribe_with_openai(audio_path: str, api_key: str, language: str = "en") -> dict:
    """Transcribe using OpenAI Whisper API."""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )
        
        return {
            "text": response.text,
            "language": response.language,
        }
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"OpenAI transcription error: {e}", file=sys.stderr)
        sys.exit(1)

def transcribe_with_assemblyai(audio_path: str, api_key: str, language: str = "en") -> dict:
    """Transcribe using AssemblyAI API."""
    try:
        import assemblyai as aai
        
        aai.settings.api_key = api_key
        
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            speaker_labels=True,
            summarization=True,
            sentiment_analysis=True,
            iab_categories=True,
        )
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path, config=config)
        
        speakers = []
        if transcript.utterances:
            for utterance in transcript.utterances:
                speakers.append({
                    "speaker": f"Speaker {utterance.speaker}",
                    "text": utterance.text,
                    "start": utterance.start / 1000,
                    "end": utterance.end / 1000,
                })
        
        return {
            "text": transcript.text,
            "speakers": speakers,
            "summary": transcript.summary,
        }
    except ImportError:
        print("Error: assemblyai package not installed. Run: pip install assemblyai", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"AssemblyAI transcription error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Cloud transcription")
    parser.add_argument("audio_path", help="Path to audio file")
    parser.add_argument("--provider", choices=["openai", "assemblyai"], required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--language", default="en")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_path):
        print(f"Error: Audio file not found: {args.audio_path}", file=sys.stderr)
        sys.exit(1)
    
    if args.provider == "openai":
        result = transcribe_with_openai(args.audio_path, args.api_key, args.language)
    else:
        result = transcribe_with_assemblyai(args.audio_path, args.api_key, args.language)
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
