import os

__version__ = os.environ.get("VERSION", "0.0.0")

parts = __version__.split(".")
if len(parts) != 3 or not all(part.isdigit() for part in parts):
    __version__ = "0.0.0"
