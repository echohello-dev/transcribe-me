import os

__version__ = os.environ.get("VERSION")

if __version__ is None:
    print("Error: VERSION environment variable is not set.")
    exit(1)
