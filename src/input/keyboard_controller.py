import ctypes
import logging

logger = logging.getLogger(__name__)

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class InputUnion(ctypes.Union):
    _fields_ = [("ki", KeyBdInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", InputUnion)]

KEYEVENT_KEYDOWN = 0x0000
KEYEVENT_KEYUP = 0x0002

VK_MAP = {
    'E': 0x45,
    'SPACE': 0x20,
    'R': 0x52
}

class KeyboardController:
    def __init__(self):
        self.pressed_keys = set()
        logger.info("Keyboard controller init")

    def press_key(self, key_str: str):
        vk = VK_MAP.get(key_str.upper())
        if not vk:
            logger.warning(f"Unknown key {key_str}")
            return

        if vk in self.pressed_keys:
            return

        ii = InputUnion()
        ii.ki = KeyBdInput(vk, 0, KEYEVENT_KEYDOWN, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(1),ii)
        SendInput(1,ctypes.pointer(command), ctypes.sizeof(command))

        self.pressed_keys.add(vk)
        logger.debug(f"Key pressed {key_str}")

    def release_key(self, key_str: str):
        vk = VK_MAP.get(key_str.upper())
        if not vk or vk not in self.pressed_keys:
            return

        ii = InputUnion
        ii.ki = KeyBdInput(vk, 0, KEYEVENT_KEYUP, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(1), ii)
        SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

        self.pressed_keys.remove(vk)
        logger.debug(f"Key released {key_str}")

    def release_all(self):
        for vk in list(self.pressed_keys):
            ii = InputUnion()
            ii.ki = KeyBdInput(vk, 0, KEYEVENT_KEYUP, 0, ctypes.pointer(ctypes.c_ulong(0)))
            command = Input(ctypes.c_ulong(1), ii)
            SendInput(1,ctypes.pointer(command), ctypes.sizeof(command))
        self.pressed_keys.clear()
        logger.debug("All keys released")