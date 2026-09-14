import mediapipe as mp
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class HandTracker:
    def __init__(self, config: dict):
        vision_cfg = config.get('vision', {})
        self.mirror = config.get('camera', {}).get('mirror', True)

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=vision_cfg.get('max_num_hands',2),
            min_detection_confidence=vision_cfg.get('min_detection_confidence', 0.7),
            min_tracking_confidence=vision_cfg.get('min_tracking_confidence', 0.5)
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_frame(self, image: np.ndarray):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2BGR)
        results = self.hands.process(image_rgb)

        hands_data = []
        if results.multi_hand_landmarks:
            for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label_mp = handedness.classification[0].label

                if self.mirror:
                    actual_hand = "right" if label_mp == "Left" else "left"
                else:
                    actual_hand = "left" if label_mp == "Left" else "right"
                hands_data.append({
                    'hand': actual_hand,
                    'landmarks': landmarks,
                    'label_mp': label_mp
                })

                self.mp_drawing.draw_landmarks(
                    image, landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

        return image, hands_data