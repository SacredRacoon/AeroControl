import cv2
import numpy as np
import logging

from .capture.camera import Camera
from .vision.tracker import HandTracker
from .vision.geometry import HandGeometry
from .vision.filter import OneEuroFilter
from .input.mouse_controller import MouseController
from .input.keyboard_controller import KeyboardController
from .input.binder import GestureBinder

logger = logging.getLogger(__name__)

class GesturePipeline:
    def __init__(self, config: dict):
        self.config = config
        self.mirror = config.get('camera', {}).get('mirror', True)

        self.camera = Camera(config)
        self.tracker = HandTracker(config)
        self.geometry = HandGeometry(config)

        self.filter_x = OneEuroFilter(config)
        self.filter_y = OneEuroFilter(config)

        self.mouse_ctrl = MouseController(config.get('input', {}).get('mouse_sensitivity', 15.0))
        self.kb_ctrl = KeyboardController()
        self.binder = GestureBinder(self.kb_ctrl, self.mouse_ctrl)

        self.target_key = str(config.get('input', {}).get('left_hand_index_key', 'E'))
        self.center_x = config.get('camera', {}).get('width', 640) // 2
        self.center_y = config.get('camera', {}).get('height', 480) // 2

    def _process_right_hand(self, landmarks):
        lm = landmarks.landmark
        raw_x = (lm[8].x * self.camera.width) - self.center_x
        raw_y = (lm[8].y * self.camera.height) - self.center_y

        smooth_x = self.filter_x.filter(raw_x)
        smooth_y = self.filter_y.filter(raw_y)

        self.mouse_ctrl.move(smooth_x, smooth_y)

        is_lclick_pinch = self.geometry.is_pinching(landmarks)
        if is_lclick_pinch:
            self.binder.execute("mouse_click_down")
        else:
            self.binder.execute("mouse_click_up")

        is_rclick_pinch = self.geometry.is_right_click_pinching(landmarks)
        if is_rclick_pinch:
            self.binder.execute("mouse_right_click_down")
        else:
            self.binder.execute("mouse_right_click_up")
    def _process_left_hand(self, landmarks):
        states = self.geometry.get_finger_states(landmarks)
        idx = bool(states.get('index', False))
        mid = bool(states.get('middle', False))
        rng = bool(states.get('ring', False))
        pnk = bool(states.get('pinky', False))
        
        if not idx and not mid and not rng and not pnk:
            self.binder.execute("release_all")
            
        elif idx and not mid and not rng and not pnk:
            self.binder.execute(f"press:{self.target_key}")
            
        elif idx and mid and not rng and not pnk:
            self.binder.execute("press:R")
            
        else:
            self.binder.execute("release_all")

    def run(self):
        logger.info("Starting pipeline")
        self.camera.start()

        try:
            while self.camera.is_running():
                frame = self.camera.read()
                if frame is None:
                    continue

                flipped_frame = cv2.flip(frame, 1) if self.mirror else frame
                
                debug_frame, hands_data = self.tracker.process_frame(flipped_frame)

                for hand_info in hands_data:
                    hand_label = hand_info['hand']
                    logger.debug(f"Hand detected: {hand_label.upper()}")

                    if hand_label == 'right':
                        self._process_right_hand(hand_info['landmarks'])
                    elif hand_label == 'left':
                        self._process_left_hand(hand_info['landmarks'])

                active_hands = [h['hand'] for h in hands_data]
                status_text = f"Mouse: {'ON' if self.mouse_ctrl.is_clicking else 'OFF'}"
                kb_text = f"KB: {self.target_key if self.kb_ctrl.pressed_keys else 'None'}"
                hands_text = f"Hands: {', '.join(active_hands).upper() if active_hands else 'NONE'}"

                cv2.putText(debug_frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(debug_frame, kb_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(debug_frame, hands_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow('Gesture control pipeline', debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")
        except Exception as e:
            import traceback
            logger.error(f"Critical error {e}\n{traceback.format_exc()}")
        finally:
            self.binder.reset()
            self.camera.stop()
            cv2.destroyAllWindows()
            logger.info("Pipeline stopped cleanly")