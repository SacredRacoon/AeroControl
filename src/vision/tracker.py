import mediapipe as mp
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

class HandTracker:
    def __init__(self, config: dict):
        vision_cfg = config.get('vision', {})
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=vision_cfg.get('max_num_hands', 2),
            min_detection_confidence=vision_cfg.get('min_detection_confidence', 0.7),
            min_tracking_confidence=vision_cfg.get('min_tracking_confidence', 0.5)
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_frame(self, image: np.ndarray):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        hands_data = []
        if results.multi_hand_landmarks:
            handedness_list = results.multi_handedness or []
            for landmarks, handedness in zip(results.multi_hand_landmarks, handedness_list):
                label = handedness.classification[0].label.lower()
                hands_data.append({'hand': label, 'landmarks': landmarks})

                self.mp_drawing.draw_landmarks(
                    image, landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        return image, hands_data