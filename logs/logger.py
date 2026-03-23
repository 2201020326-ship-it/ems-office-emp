"""Central logging configuration for EMS."""

import logging
from pathlib import Path

_LOG_FILE = Path(__file__).resolve().parent / "ems.log"


def _configure_root_logger() -> None:
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("ems")
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)


def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(f"ems.{name}")
