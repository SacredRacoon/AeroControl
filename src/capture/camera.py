import cv2 
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self,config:dict):
        self.camera_cfg = config.get('camera',{})
        self.width = self.camera_cfg.get('width', 640)
        self.height = self.camera_cfg.get('height', 480)
        self.fps_target = self.camera_cfg.get('fps_target',60)
        self.device_id = self.camera_cfg.get('device_id', 0)

        self.cap: Optional[cv2.VideoCapture] = None
        self._is_running = False

        logger.info(f"Camera module init {self.width} x {self.height}, fps {self.fps_target}")

    def start(self) -> bool:
        logger.info(f"Attempt to open camera {self.device_id}")
        self.cap = cv2.VideoCapture(self.device_id)

        if not self.cap.isOpened():
            logger.error(f"failed to open camera {self.device_id}")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)

        actual_width = int(self.cap.set(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self.cap.set(cv2.CAP_PROP_FPS))

        logger.info(f"Camera opened, res {actual_width} x {actual_height}, fps {actual_fps}")
        self._is_running = True
        return True

    def read(self) -> Optional[np.ndarray]:
        if not self._is_running or self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame")
            return None

        return frame

    def stop(self) -> None:

        if self.cap is not None:
            logger.info('Release camera resources')
            self.cap.release()
            self.cap = None

        self._is_running = False
        logger.info("Camera stopped")

    def is_running(self) -> bool:
        return self._is_running and (self.cap is not None) and self.cap.isOpened()