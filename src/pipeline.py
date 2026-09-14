import cv2
import numpy as np
import time 
import logging

from .capture.camera import Camera
from .vision.tracker import HandTracker
from .vision.geometry import HandGeometry
from .vision.filter import OneEuroFilter
from .input.mouse_controller import MouseController
from .input.keyboard_controller import KeyboardController

logger = logging.getLogger(__name__)

class GesturePipeline:
    def __init__(self,config: dict):
        self.config = config
        self.camera = Camera(config)
        self.tracker = HandTracker(config)
        self.geometry = HandGeometry(config)

        self.filter_x = OneEuroFilter(config)
        self.filter_y = OneEuroFilter(config)

        self.mouse_ctrl = MouseController(config.get('input', {}).get('mouse_sensitivity', 15.0))
        self.kb_ctrl = KeyboardController()

        self.target_key = config.get('input', {}).get('left_hand_index_key', 'E')
        self.center_x = config.get('camera', {}).get('width', 640) // 2
        self.center_y = config.get('camera', {}).get('height', 480) //2

    def _process_right_hand(self,landmarks):
        lm = landmarks.landmark

        raw_x = (lm[8].x * self.camera.width) - self.center_x
        raw_y = (lm[8].y * self.camera.height - self.center_y)

        smooth_x = self.filter_x.filter(raw_x)
        smooth_y = self.filter_y.filter(raw_y)

        self.mouse_ctrl.move(smooth_x, smooth_y)

        is_pinch = self.geometry.is_pinching(landmarks)
        self.mouse_ctrl.click(is_pinch)

    def _process_left_hand(self,landmarks):
        states = self.geometry.get_finger_states(landmarks)

        is_fist = not states['index'] and not states['middle'] and not states['ring'] and not states ['pinky']
        is_index_up = states['index'] and not states['middle'] and not states['ring'] and not states ['pinky']

        if is_fist:
            self.kb_ctrl.release_all()
        elif is_index_up:
            self.kb_ctrl.press_key(self.target_key)
        else:
            self.kb_ctrl.release_all()

    def run(self):
        self.camera.start()

        try:
            while self.camera.is_running():
                frame = self.camera.read()
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)

                debug_frame, hands_data = self.tracker.process_frame(frame)

                for hand_info in hands_data:
                    if hand_info['hand'] == 'right':
                        self._process_right_hand(hand_info['landmarks'])
                    elif hand_info['hand'] == 'left':
                        self._process_left_hand(hand_info['landmarks'])

                cv2.putText(debug_frame, f"Mouse click {'ON' if self.mouse_ctrl.is_clicking else 'OFF'}",
                            (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)
                cv2.putText(debug_frame, f"KB Active {self.target_key if self.kb_ctrl.pressed_keys else 'None'}",
                            (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

                cv2.imshow('Gesture control pipeline', debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")
        finally:
            self.kb_ctrl.release_all()
            self.camera.stop()
            cv2.destroyAllWindows()
            logger.info("Pipeline stopped cleanly")