from pathlib import Path

class PathManager:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(file__).resolve().parent.parent.parent
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.output_dir / "logs"
        self.calibration_dir = self.output_dir / "calibration"

    def create_dirs(self):
        for directory in [self.output_dir, self.logs_dir, self.calibration_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        return self