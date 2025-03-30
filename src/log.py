""" 
    File: log.py
    Desc: Daemon utility logger.
"""

import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.FileHandler("spotify-remote.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Overall application logger.
AppLogger = logging.getLogger("SpotifyGestureControl")
