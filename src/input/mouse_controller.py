import ctypes
import logging
from ctypes import wintypes

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

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx",wintypes.LONG), 
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), 
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), 
                ("dwExtraInfo", ctypes.c_void_p)
                ]

class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), 
                ("union", _INPUTUNION)
                ]

class MouseController:
    def __init__(self, sensitivity: float):
        self.sensitivity = sensitivity
        self.is_clicking = False
        logger.info("Mouse controller init")

    def move(self, dx: float, dy: float):
        if abs(dx) < 1 and abs(dy) <1:
            return

        dx_int = int(dx / self.sensitivity)
        dy_int = int(dy / self.sensitivity)

        ii = _INPUTUNION()
        ii.mi = MOUSEINPUT(dx_int, dy_int, 0, MOUSEEVENTF_MOVE, 0, ctypes.c_void_p(0))
        command = INPUT(INPUT_MOUSE, ii)

        result = SendInput(1, ctypes.byref(command), ctypes.sizeof(command))
        if result == 0:
            err = ctypes.get_last_error()
            logger.error(f"SendInput mouse_move failed winerr {err}")

    def click_left(self, press: bool):
        flag = MOUSEEVENTF_LEFTDOWN if press else MOUSEEVENTF_LEFTUP
        self._send_mouse_event(flag, "LEFT")
        
    def click_right(self, press: bool):
        flag = MOUSEEVENTF_RIGHTDOWN if press else MOUSEEVENTF_RIGHTUP
        self._send_mouse_event(flag, "RIGHT")

    def _send_mouse_event(self, flag: int, btn_name: str):
        ii = _INPUTUNION()
        ii.mi = MOUSEINPUT(0, 0, 0, flag, 0, ctypes.c_void_p(0))
        command = INPUT(INPUT_MOUSE, ii)

        result = SendInput(1, ctypes.byref(command), ctypes.sizeof(command))
        if result == 0:
            err = ctypes.get_last_error()
            logger.error(f"SendInput {btn_name} failed winerr {err}")
        else:
            logger.debug(f"Mouse {btn_name} {'PRESSED' if flag in (2, 8) else 'RELEASED'}")