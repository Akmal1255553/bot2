import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

from config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(lineno)d"
    formatter = jsonlogger.JsonFormatter(log_format)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.log_level.upper())

    # Console handler (stdout) — visible via journalctl
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    log_dir = os.path.dirname(settings.log_file_path)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=settings.log_file_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.getLogger("aiogram").setLevel(settings.log_level.upper())
