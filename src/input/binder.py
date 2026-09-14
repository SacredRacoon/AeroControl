import logging

logger = logging.getLogger(__name__)

class GestureBinder:
    def __init__(self,kb_ctrl, mouse_ctrl):
        self.kb = kb_ctrl
        self.mouse = mouse_ctrl
        self.active_keys = set()
        self.is_mouse_clicking = False
        self.is_mouse_right_clicking = False

    def execute(self, action: str):
        if not action:
            return

        if action == "release_all":
            self.kb.release_all()
            self.active_keys.clear()
            return

        if action.startswith("press:"):
            key = action.split(":",1)[1]
            if key not in self.active_keys:
                self.kb.press_key(key)
                self.active_keys.add(key)
            return

        if action.startswith("release:"):
            key = action.split(":",1)[1]
            if key in self.active_keys:
                self.kb.release_key(key)
                self.active_keys.remove(key)
            return

        if action == "mouse_click_down":
            if not self.is_mouse_clicking:
                self.mouse.click_left(True)
                self.is_mouse_clicking = True
        elif action == "mouse_click_up":
            if self.is_mouse_clicking:
                self.mouse.click_left(False)
                self.is_mouse_clicking = False
                
        elif action == "mouse_right_click_down":
            if not self.is_mouse_right_clicking:
                self.mouse.click_right(True)
                self.is_mouse_right_clicking = True
        elif action == "mouse_right_click_up":
            if self.is_mouse_right_clicking:
                self.mouse.click_right(False)
                self.is_mouse_right_clicking = False
    def reset(self):
        self.kb.release_all()
        if self.is_mouse_clicking:
            self.mouse.click(False)
            self.is_mouse_clicking = False
        self.active_keys.clear()
