""" 
    File: main.py
    Desc: Main daemon entry. 
"""
import dotenv
import spotify
import sys

from log import AppLogger
from spotify import SpotifyHandler

# Main application entry point.
if __name__ == "__main__":
    AppLogger.debug("Initializing main application.")

    if not dotenv.load_dotenv(verbose=True):
        AppLogger.error("UNRECOVERABLE: Unable to access environmental variables. Exiting...")
        sys.exit(1)

    AppLogger.debug("Succesfully initialized, entering the main application loop.")
    pass
