""" 
    File: main.py
    Desc: Main daemon entry. 
"""
import dotenv
import spotify
import sys

import cv2
from gestureControl import GestureControl

from log import AppLogger
from spotify import SpotifyHandler

# Main application entry point.
if __name__ == "__main__":
    AppLogger.debug("Initializing main application.")

    if not dotenv.load_dotenv(verbose=True):
        AppLogger.error("UNRECOVERABLE: Unable to access environmental variables. Exiting...")
        sys.exit(1)

    cap = cv2.VideoCapture(0)
    gesture_control = GestureControl()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame = gesture_control.process_frame(frame)
        
        cv2.imshow('Gesture Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    AppLogger.debug("Succesfully initialized, entering the main application loop.")
    pass
