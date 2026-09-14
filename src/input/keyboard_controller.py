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
    'E': 0x45, 'R': 0x52, 'Q': 0x51, 'F': 0x46, 'C': 0x43,
    'SPACE': 0x20, 'SHIFT': 0xA0, 'CTRL': 0xA2, 'ALT': 0xA4,
    '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
    'TAB': 0x09, 'ENTER': 0x0D, 'ESC': 0x1B 
}

class KeyboardController:
    def __init__(self):
        self.pressed_keys = set()
        logger.info("Keyboard controller init")

    def press_key(self, key_str: str):
        key_name = str(key_str).upper().strip()
        vk_code = VK_MAP.get(key_name)

        if not vk_code:
            logger.warning(f"Unknown key {key_str}")
            return

        if vk_code in self.pressed_keys:
            return

        logger.debug(f"Key pressed {key_str} (0x{vk_code:02X})")

        ii = InputUnion()
        ii.ki = KeyBdInput(vk_code, 0, KEYEVENT_KEYDOWN, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(1),ii)
        SendInput(1,ctypes.pointer(command), ctypes.sizeof(command))
        result = SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
        if result == 0:
            logger.error("SendInput keydown failed")
        self.pressed_keys.add(vk_code)

    def release_key(self, key_str: str):
        key_name = str(key_str).upper().strip()
        vk_code = VK_MAP.get(key_str.upper())

        if vk_code is None or vk_code not in self.pressed_keys:
            return

        logger.debug(f"Key released {key_name}")

        ii = InputUnion()
        ii.ki = KeyBdInput(vk_code, 0, KEYEVENT_KEYUP, 0, ctypes.pointer(ctypes.c_ulong(0)))
        command = Input(ctypes.c_ulong(1), ii)
        SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))
        result = SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))

        if result == 0:
            logger.error("SendInput keyup failed")
        self.pressed_keys.remove(vk_code)

    def release_all(self):
        if not self.pressed_keys:
            return

        logger.info("All keys released")
        for vk_code in list(self.pressed_keys):
            ii = InputUnion()
            ii.ki = KeyBdInput(vk_code, 0, KEYEVENT_KEYUP, 0, ctypes.pointer(ctypes.c_ulong(0)))
            command = Input(ctypes.c_ulong(1), ii)
            SendInput(1,ctypes.pointer(command), ctypes.sizeof(command))

        self.pressed_keys.clear()