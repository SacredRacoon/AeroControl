import ctypes
import logging
from ctypes import wintypes

logger = logging.getLogger(__name__)

SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
SendInput.restype = wintypes.UINT

INPUT_KEYBOARD = 1
KEYEVENT_KEYDOWN = 0x0000
KEYEVENT_KEYUP = 0x0002

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wWk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)
                ]
class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), 
                ("union", _INPUTUNION)
                ]



VK_MAP = {
    'E': 0x45, 'R': 0x52, 'Q': 0x51, 'F': 0x46, 'C': 0x43,
    'SPACE': 0x20, 'SHIFT': 0xA0, 'CTRL': 0xA2, 'ALT': 0xA4,
    '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
    'TAB': 0x09, 'ENTER': 0x0D, 'ESC': 0x1B , 'W': 0x57, 'A': 0x41, 'S': 0x53, 'D': 0x44
}

class KeyboardController:
    def __init__(self):
        self.pressed_keys = set()
        logger.info("Keyboard controller init")

    def press_key(self, key_str: str):
        key_name = str(key_str).upper().strip()
        vk_code = VK_MAP.get(key_name)
        if not vk_code or vk_code in self.pressed_keys:
            return

        ii = _INPUTUNION()
        ii.ki = KEYBDINPUT(vk_code, 0, KEYEVENT_KEYDOWN, 0, ctypes.c_void_p(0))
        command = INPUT(INPUT_KEYBOARD,ii)

        result = SendInput(1, ctypes.byref(command), ctypes.sizeof(command))
        if result == 0:
            err = ctypes.get_last_error()
            logger.error(f"SendInput keydown failed {key_name} winerr {err}")
        else:
            self.pressed_keys.add(vk_code)
            logger.debug(f"Key pressed {key_name}")

    def release_key(self, key_str: str):
        key_name = str(key_str).upper().strip()
        vk_code = VK_MAP.get(key_name)
        if vk_code is None or vk_code not in self.pressed_keys:
            return

        ii = _INPUTUNION()
        ii.ki = KEYBDINPUT(vk_code, 0, KEYEVENT_KEYUP, 0, ctypes.c_void_p(0))
        command = INPUT(INPUT_KEYBOARD,ii)

        result = SendInput(1, ctypes.byref(command), ctypes.sizeof(command))
        if result == 0:
            err = ctypes.get_last_error()
            logger.error(f"SendInput keydup failed {key_name} winerr {err}")
        else:
            self.pressed_keys.remove(vk_code)
            logger.debug(f"Key released {key_name}")

    def release_all(self):
        if not self.pressed_keys:
            return

        logger.info("All keys released")

        for vk_code in list(self.pressed_keys):
            ii = _INPUTUNION()
            ii.ki = KEYBDINPUT(vk_code, 0, KEYEVENT_KEYUP, 0, ctypes.pointer(ctypes.c_void_p(0)))
            command = INPUT(INPUT_KEYBOARD.c_ulong(1), ii)
            SendInput(1,ctypes.byref(command), ctypes.sizeof(command))

        self.pressed_keys.clear()