""" 
    File: log.py
    Desc: Daemon utility logger.
"""

import logging
import sys
import os

DBG_MODE = os.getenv("SPOTIFY_REMOTE_DEBUG_MODE", default="True")

logging.basicConfig(
    level=logging.DEBUG if bool(DBG_MODE) else logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("spotify-remote.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Overall application logger.
AppLogger = logging.getLogger("SpotifyGestureControl")
