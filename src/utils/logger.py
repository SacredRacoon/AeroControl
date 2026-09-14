import logging
from pathlib import Path

def setup_logger(log_file: Path, level=logging.DEBUG):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("global log init")
    return root_logger