#!/usr/bin/env python3
"""
Download and cache parakeet-mlx models from Hugging Face.
"""

import argparse
import sys
import os
from pathlib import Path

def download_model(model_id: str, cache_dir: str = None) -> str:
    """Download a parakeet-mlx model."""
    try:
        from parakeet_mlx import from_pretrained
        
        print(f"Downloading model: {model_id}")
        print("This may take a few minutes depending on your connection...")
        
        # Load model (this triggers download)
        kwargs = {}
        if cache_dir:
            kwargs['cache_dir'] = cache_dir
            
        model = from_pretrained(model_id, **kwargs)
        
        print(f"Model downloaded successfully!")
        return model_id
    except ImportError:
        print("Error: parakeet-mlx not installed. Run: pip install parakeet-mlx", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Download error: {e}", file=sys.stderr)
        sys.exit(1)

def list_available_models():
    """List available parakeet models."""
    models = [
        "mlx-community/parakeet-tdt-0.6b-v3",
        "mlx-community/parakeet-tdt-1.1b",
        "mlx-community/parakeet-rnnt-0.6b",
        "mlx-community/parakeet-ctc-0.6b",
        "mlx-community/parakeet-tdt-ctc-0.6b",
    ]
    
    print("Available models:")
    for model in models:
        print(f"  - {model}")
    
    print("\nRecommended: mlx-community/parakeet-tdt-0.6b-v3 (best balance of speed and accuracy)")

def main():
    parser = argparse.ArgumentParser(description="Download parakeet-mlx models")
    parser.add_argument("model_id", nargs="?", help="Model ID to download")
    parser.add_argument("--cache-dir", help="Custom cache directory")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_models()
        return
    
    if not args.model_id:
        print("Error: Please specify a model ID or use --list", file=sys.stderr)
        sys.exit(1)
    
    download_model(args.model_id, args.cache_dir)

if __name__ == "__main__":
    main()
