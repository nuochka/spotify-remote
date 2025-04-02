""" 
    File: gestureControl.py
    Decs: Handles whole gesture control logic via mediapipe wrapper. 
"""

import mediapipe as mp
import cv2
import time

from enum import Enum
from log import AppLogger

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

class GestureAction(Enum):
    NEXT_TRACK = "next track"
    PREV_TRACK = "prev track"
    PLAY_PAUSE = "play/pause"
    NONE = "none"

class GestureControl:
    def __init__(self, action_cooldown=2, quick_action_cooldown=0.3):
        self.hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.quick_action_cooldown = quick_action_cooldown
        self.action_cooldown = action_cooldown
        self.last_action_time = 0
        self.current_state = GestureAction.NONE

    # Counts the amount of fingers seen on the screen.
    def count_fingers(self, hand_landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_folded = [hand_landmarks.landmark[i].y > hand_landmarks.landmark[i - 2].y for i in finger_tips]
        return finger_folded.count(False)
    
    """ 
        Processes the currently obtained frame from the video camera.
    """
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers = self.count_fingers(hand_landmarks)
                
                current_time = time.time()
                if current_time - self.last_action_time > self.cooldown:
                    if fingers == 1:
                        self.current_state = GestureAction.NEXT_TRACK
                        AppLogger.debug("Gesture detected: NEXT_TRACK")
                    elif fingers == 2:
                        self.current_state = GestureAction.PREV_TRACK
                        AppLogger.debug("Gesture detected: PREV_TRACK")
                    elif fingers == 5:
                        self.current_state = GestureAction.PLAY_PAUSE
                        AppLogger.debug("Gesture detected: PLAY_PAUSE")
                    else:
                        self.last_action_time = current_time
                        AppLogger.debug("No valid gesture detected.")
        return frame
