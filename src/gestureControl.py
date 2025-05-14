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
    VOLUME_SET = "volume set"
    NONE = "none"

    def __init__(self, value=None) -> None:
        self._volume_set_value = value

    @property
    def volume(self):
        return self._volume_set_value

    @volume.setter
    def volume_percentage(self, volume):
        self._volume_set_value = volume

class GestureControl:
    def __init__(self, action_cooldown=2, quick_action_cooldown=0.3, volume_cooldown=1.0):
        self.hands = mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.quick_action_cooldown = quick_action_cooldown  # for frequent actions like volume control
        self.action_cooldown = action_cooldown  # for less frequent actions like track change, play/pause
        self.volume_cooldown = volume_cooldown  # additional cooldown for volume control

        # Individual cooldown timestamps for different actions
        self.last_play_pause_time = 0
        self.last_next_track_time = 0
        self.last_prev_track_time = 0
        self.last_volume_set_time = 0
        
        self.current_state = GestureAction.NONE

    '''
        Counts the amount of fingers seen on the screen.
    '''
    def count_fingers(self, hand_landmarks):
        finger_tips = [4, 8, 12, 16, 20]
        finger_folded = [hand_landmarks.landmark[i].y > hand_landmarks.landmark[i - 2].y for i in finger_tips]
        return finger_folded.count(False)

    """
        Detects if a full hand is being shown to the camera (all fingers open).
    """
    def detect_full_hand(self, hand_landmarks):
        return self.count_fingers(hand_landmarks) == 5
   
    """
        Detects the direction of the thumb for NEXT_TRACK and PREV_TRACK actions.
    """
    def detect_thumb_direction(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        thumb_base = hand_landmarks.landmark[2]
    
        thumb_vector_x = thumb_tip.x - thumb_base.x
    
        if thumb_vector_x > 0.1:
            return GestureAction.NEXT_TRACK
        elif thumb_vector_x < -0.1:
            return GestureAction.PREV_TRACK
        else:
            return GestureAction.NONE

    def calculate_distance(self, point1, point2):
        # Calculate the Euclidean distance between two points
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2) ** 0.5

    """
        Detects volume control gesture based on the distance between the thumb and pinky.
    """
    def detect_volume_gesture(self, hand_landmarks):
        # Detect volume control gesture based on thumb and pinky distance
        thumb_tip = hand_landmarks.landmark[4]
        pinky_tip = hand_landmarks.landmark[20]
        
        # Calculate the distance between thumb and pinky
        distance = self.calculate_distance(thumb_tip, pinky_tip)
        
        # Normalize the distance for volume control (you can adjust the factor for sensitivity)
        volume_percentage = min(100, int(distance * 200))  # Example scaling factor
        
        return volume_percentage

    def process_frame(self, frame, debug=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.current_state = GestureAction.NONE
        results = self.hands.process(rgb_frame)
    
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
    
            if debug:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
            current_time = time.time()

            # Detect Next/Prev track
            gesture = self.detect_thumb_direction(hand_landmarks)
            if gesture != GestureAction.NONE:
                if gesture == GestureAction.NEXT_TRACK and (current_time - self.last_next_track_time) > self.action_cooldown:
                    if self.count_fingers(hand_landmarks) < 2:
                        self.last_next_track_time = current_time
                        self.current_state = GestureAction.NEXT_TRACK
                        AppLogger.debug("Thumb gesture detected: NEXT_TRACK")
                        return frame
                
                elif gesture == GestureAction.PREV_TRACK and (current_time - self.last_prev_track_time) > self.action_cooldown:
                    if self.count_fingers(hand_landmarks) < 2:
                        self.last_prev_track_time = current_time
                        self.current_state = GestureAction.PREV_TRACK
                        AppLogger.debug("Thumb gesture detected: PREV_TRACK")
                        return frame

            # Detect Play/Pause gesture: Full hand open to camera
            if self.detect_full_hand(hand_landmarks):
                if current_time - self.last_play_pause_time > self.action_cooldown:
                    self.last_play_pause_time = current_time
                    self.current_state = GestureAction.PLAY_PAUSE
                    AppLogger.debug("Gesture detected: PLAY_PAUSE")
                    return frame

            # Detect Volume control gesture: Based on the distance between thumb and pinky
            volume_percentage = self.detect_volume_gesture(hand_landmarks)
            if current_time - self.last_volume_set_time > self.volume_cooldown:
                # Only update the volume if no other gesture (track or play/pause) is being processed
                if self.current_state == GestureAction.NONE or self.current_state == GestureAction.VOLUME_SET:
                    # Only update the volume if it is different from the current state
                    if volume_percentage != self.current_state.volume:
                        self.last_volume_set_time = current_time
                        # Set the volume correctly using the setter
                        self.current_state = GestureAction.VOLUME_SET
                        self.current_state.volume_percentage = volume_percentage  # Correctly set volume

                        AppLogger.debug(f"Volume gesture detected: {volume_percentage}%")

        return frame
