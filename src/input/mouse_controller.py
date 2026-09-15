import ctypes
import logging
from ctypes import wintypes
import numpy as np
import time

logger = logging.getLogger(__name__)

SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
SendInput.restype = wintypes.UINT

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), 
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), 
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), 
                ("dwExtraInfo", ctypes.c_void_p)
                ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]

class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), 
                ("union", _INPUTUNION)
                ]

class MouseController:
    def __init__(self, config: dict):
        # ЗАЩИТА: если в YAML написано просто число, мы принудительно делаем его словарем
        mouse_cfg = config.get('mouse', {})
        if not isinstance(mouse_cfg, dict):
            mouse_cfg = {}
            
        self.sensitivity = mouse_cfg.get('sensitivity', 12.0)
        self.acceleration = mouse_cfg.get('acceleration', 0.03)
        self.dead_zone = mouse_cfg.get('dead_zone', 8.0)
        self.max_move = mouse_cfg.get('max_move_per_frame', 80)
        self.click_debounce = mouse_cfg.get('click_debounce', 0.12)

        self.is_clicking = False
        self.is_right_clicking = False
        self.last_click_change_time = 0

        self.extra_info = ctypes.c_void_p(0)
        logger.info("Mouse controller init")

    def _apply_curve(self, dx: float, dy: float) -> tuple:
        dist = np.hypot(dx, dy)
        if dist < self.dead_zone:
            return 0.0, 0.0

        base_speed = 1.0 / self.sensitivity

        accel_multiplier = 1.0 + min(self.acceleration * dist, 5.0)
        final_factor = base_speed * accel_multiplier

        move_x = dx * final_factor
        move_y = dy * final_factor

        move_dist = np.hypot(move_x, move_y)
        if move_dist > self.max_move:
            scale = self.max_move / move_dist
            move_x *= scale
            move_y *= scale

        return int(move_x), int(move_y)
    
    def move(self, dx: float, dy: float):
        dx_int, dy_int = self._apply_curve(dx, dy)
        if dx_int == 0 and dy_int == 0:
            return

        ii = _INPUTUNION()
        ii.mi = MOUSEINPUT(dx_int, dy_int, 0, MOUSEEVENTF_MOVE, 0, self.extra_info)
        command = INPUT(INPUT_MOUSE, ii)
        SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

    def _send_click(self, flag: int):
        ii = _INPUTUNION()
        ii.mi = MOUSEINPUT(0, 0, 0, flag, 0, self.extra_info)
        command = INPUT(INPUT_MOUSE, ii)
        SendInput(1, ctypes.byref(command), ctypes.sizeof(command))

    def click_left(self, is_pinching: bool):
        current_time = time.time()
        if current_time - self.last_click_change_time < self.click_debounce:
            return

        if is_pinching and not self.is_clicking:
            self.is_clicking = True
            self.last_click_change_time = current_time
            self._send_click(MOUSEEVENTF_LEFTDOWN)
            logger.debug("LMB pressed")

        elif not is_pinching and self.is_clicking:
            self.is_clicking = False
            self.last_click_change_time = current_time
            self._send_click(MOUSEEVENTF_LEFTUP)
            logger.debug("LMB released")
        
    def click_right(self, is_pinching: bool):
        current_time = time.time()
        if current_time - self.last_click_change_time < self.click_debounce:
            return

        if is_pinching and not self.is_right_clicking:
            self.is_right_clicking = True
            self.last_click_change_time = current_time
            self._send_click(MOUSEEVENTF_RIGHTDOWN)
            logger.debug("RMB pressed")

        elif not is_pinching and self.is_right_clicking:
            self.is_right_clicking = False
            self.last_click_change_time = current_time
            self._send_click(MOUSEEVENTF_RIGHTUP)
            logger.debug("RMB released")

    def release_all(self):
        if self.is_clicking:
            self._send_click(MOUSEEVENTF_LEFTUP)
            self.is_clicking = False
        if self.is_right_clicking:
            self._send_click(MOUSEEVENTF_RIGHTUP)
            self.is_right_clicking = False
        logger.info("Mouse buttons released")