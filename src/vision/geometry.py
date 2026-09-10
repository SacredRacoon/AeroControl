import numpy as np
import logging

logger = logging.getLogger(__name__)

class HandGeometry:
    def __init__(self, config: dict):
        self.ext_angle = config.get('geometry', {}).get('finger_extension_angle', 150)
        self.bend_angle = config.get('geometry', {}).get('finger_bend_angle',130)
        self.pinch_thresh = config.get('geometry', {}).get('pinch_threshold', 0.05)

    def _calculate_angle(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
        return angle

    def get_finger_states(self, landmarks) -> dict:
        lm = landmarks.landmark

        def get_coords(idx):
            return np.array([lm[idx].x, lm[idx].y, lm[idx].z])

        states = {}

        dist_thumb = np.linalg.norm(get_coords(4) - get_coords(5))
        states['thumb'] = dist_thumb > 0.15

        finger_indices = {
            'index': (5, 6, 8),
            'middle': (9, 10, 12),
            'ring': (13, 14, 16),
            'pinky': (17, 18, 20)
        }

        for name, (mcp, pip, dip) in finger_indices.items():
            angle = self._calculate_angle(get_coords(mcp), get_coords(pip), get_coords(dip))
            states[name] = angle > self.ext_angle

        return states

    def is_pinching(self, landmarks) -> bool:
        lm = landmarks.landmark
        thumb_tip = np.array([lm[4].x, lm[4].y])
        index_tip = np.array([lm[8].x, lm[8].y])
        distance = np.linalg.norm(thumb_tip - index_tip)
        return distance < self.pinch_thresh