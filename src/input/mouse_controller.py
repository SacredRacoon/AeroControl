import ctypes
import logging

logger = logging.getLogger(__name__)

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]

class InputUnion(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", InputUnion)]

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

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

        ii = InputUnion()
        ii.mi = MouseInput(dx_int, dy_int, 0, MOUSEEVENTF_MOVE, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(0), ii)
        SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

    def click(self, press: bool):
        if press == self.is_clicking:
            return

        flag = MOUSEEVENTF_LEFTDOWN if press else MOUSEEVENTF_LEFTUP
        ii = InputUnion()
        ii.mi = MouseInput(0, 0, 0, flag, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(0), ii)
        SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

        self.is_clicking = press
        logger.debug(f"Mouse l-click {'PRESSED' if press else 'RELEASED'}")