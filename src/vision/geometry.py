import numpy as np
import logging

logger = logging.getLogger(__name__)

class HandGeometry:
    def __init__(self, config: dict):
        geom_cfg = config.get('geometry', {})

        self.finger_thresholds = {
            'index': geom_cfg.get('threshold_index', 155),
            'middle': geom_cfg.get('threshold_middle', 145),
            'ring': geom_cfg.get('threshold_ring',145),
            'pinky': geom_cfg.get('threshold_pinky',140),
            'thumb': geom_cfg.get('threshold_thumb', 0.12)
        }

        self.pinch_ratio_thresh = geom_cfg.get('pinch_ratio_threshold', 0.15)

    def _calculate_angle(self, a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

    def _is_finger_extended(self, mcp, pip, dip, threshold: float) -> bool:
        angle = self._calculate_angle(mcp,pip,dip)
        if angle < threshold:
            return False
        if dip[1] > mcp[1] + 0.02:
            return False
        return True

    def get_finger_states(self, landmarks) -> dict:
        lm = landmarks.landmark

        def get_2d(idx):
            return np.array([lm[idx].x, lm[idx].y])

        states = {}

        thumb_tip = get_2d(4)
        index_mcp = get_2d(5)

        states['thumb'] = np.linalg.norm(thumb_tip - index_mcp) > self.finger_thresholds['thumb']

        finger_indices = {
            'index': (5, 6, 8),
            'middle': (9, 10, 12),
            'ring': (13, 14, 16),
            'pinky': (17, 18, 20)
        }

        for name, (mcp_idx, pip_idx, dip_idx) in finger_indices.items():
            mcp = get_2d(mcp_idx)
            pip = get_2d(pip_idx)
            dip = get_2d(dip_idx)
            states[name] = self._is_finger_extended(mcp, pip, dip, self.finger_thresholds[name])

        return states

    def _get_hand_size(self,landmarks) -> float:
        lm = landmarks.landmark
        wrist = np.array([lm[0].x, lm[0].y])
        middle_mcp = np.array([lm[9].x, lm[9].y])
        return np.linalg.norm(wrist - middle_mcp)

    def is_pinching(self, landmarks) -> bool:
        lm = landmarks.landmark
        thumb_tip = np.array([lm[4].x, lm[4].y])
        index_tip = np.array([lm[8].x, lm[8].y])

        pinch_dist = np.linalg.norm(thumb_tip - index_tip)
        hand_size = self._get_hand_size(landmarks)

        if hand_size < 0.01:
            return False
        
        return (pinch_dist / hand_size) < self.pinch_ratio_thresh

    def is_right_click_pinching(self, landmarks) -> bool:
        lm = landmarks.landmark
        thumb_tip = np.array([lm[4].x, lm[4].y])
        middle_tip = np.array([lm[12].x, lm[12].y])

        pinch_dist = np.linalg.norm(thumb_tip - middle_tip)
        hand_size = self._get_hand_size(landmarks)

        if hand_size < 0.01:
            return False
        
        return (pinch_dist / hand_size) < self.pinch_ratio_thresh