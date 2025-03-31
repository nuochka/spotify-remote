import cv2
import mediapipe as mp
import numpy as np
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

class GestureControl:
    def __init__(self, cooldown=2):
        self.hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.last_action_time = 0
        self.cooldown = cooldown

    def count_fingers(self, hand_landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_folded = [hand_landmarks.landmark[i].y > hand_landmarks.landmark[i - 2].y for i in finger_tips]
        return finger_folded.count(False)
    
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
                        print("next track")
                    elif fingers == 2:
                        print("prev track")
                    elif fingers == 5:
                        print("play/pause")
                    self.last_action_time = current_time
        return frame
