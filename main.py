import logging 
from pathlib import Path
from src.utils.paths import PathManager
from src.utils.config_loader import Config
from src.utils.logger import setup_logger
from src.pipeline import GesturePipeline
def main():
    path_manager = PathManager().create_dirs()
    config = Config("config.yaml")

    log_file = path_manager.logs_dir / "app.log"
    logger = setup_logger(log_file, level=logging.INFO)

    logger.info("Start aerocontrol app")
    config.print_config()
    
    try:
        pipeline = GesturePipeline(config.config)
        pipeline.run()

    except Exception as e:
        logger.error(f"Critical error in pipeline {e}")
    finally:
        logger.info("App closed")

if __name__ == "__main__":
    main()

