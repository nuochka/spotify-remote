""" 
    File: main.py
    Desc: Main daemon entry. 
"""
import dotenv
import time
import sys
import os 

import cv2
import spotify

from log import AppLogger
from spotify import SpotifyHandler
from gestureControl import GestureControl, GestureAction 

CAM_TIMEOUT     = os.getenv("SPOTIFY_REMOTE_CAMERA_TIMEOUT", default="15")
DBG_MODE        = os.getenv("SPOTIFY_REMOTE_DEBUG_MODE", default="True")

# Main application entry point.
if __name__ == "__main__":
    AppLogger.debug("Initializing main application.")

    # Spotify API related values must always be properly loaded. 
    if not dotenv.load_dotenv(verbose=True):
        AppLogger.fatal("UNRECOVERABLE: Unable to access environmental variables. Exiting...")
        sys.exit(1)


    try:
        spot = SpotifyHandler()
        gesture_ctrl = GestureControl()

        AppLogger.debug("Succesfully initialized, entering the main application loop.")
        while True:
            cap = cv2.VideoCapture(0)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    AppLogger.warning("Lost communication with video camera.")
                    break

                frame = cv2.flip(frame, 1)
                frame = gesture_ctrl.process_frame(frame, bool(DBG_MODE))

                match gesture_ctrl.current_state:
                    case GestureAction.NEXT_TRACK:
                        spot.perform(spotify.SPOTIFY_NEXT_TRACK)
                    case GestureAction.PREV_TRACK:
                        spot.perform(spotify.SPOTIFY_PREV_TRACK)
                    case GestureAction.PLAY_PAUSE:
                        if spot.current:
                            if spot.current['is_playing']:
                                spot.perform(spotify.SPOTIFY_PAUSE_TRACK)
                            else:
                                spot.perform(spotify.SPOTIFY_RESUME_TRACK)

                if bool(DBG_MODE):  # Reference window is only available in debug mode.
                    cv2.imshow('Gesture Control', frame)
                    cv2.waitKey(1)

            cap.release()
            if bool(DBG_MODE):
                cv2.destroyAllWindows()

            AppLogger.error(f'Unable to access camera device. Retrying in {CAM_TIMEOUT} seconds.')
            time.sleep(int(CAM_TIMEOUT))
    except Exception as e:
        AppLogger.fatal(f'UNRECOVERABLE: Unhandled error occured: {e}')
    finally:
        AppLogger.info("Stopping the spotify-remote daemon...")
