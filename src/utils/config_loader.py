import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def print_config(self):
        print("Aerocontrol control config")
        cam = self.get('camera') or {}
        print(f"Camera {cam.get('width')}x{cam.get('height')}, fps {cam.get('fps_target')}, mirror {cam.get('mirror')}")

        vis = self.get('vision') or {}
        print(f"Vision Max Hands {vis.get('max_num_hands')}, det conf {vis.get('min_detection_confidence')}")
        
        geom = self.get('geometry') or {}
        print(f"Geometry Extension > {geom.get('finger_extension_angle')}, Bend < {geom.get('finger_bend_angle')}")
        
        inp = self.get('input') or {}
        print(f"Input Mouse sens {inp.get('mouse_sensitivity')}, Left Key '{inp.get('left_hand_index_key')}'")
        
        flt = self.get('filter') or {}
        print(f"Filter Min Cutoff {flt.get('min_cutoff')}, Beta: {flt.get('beta')}")