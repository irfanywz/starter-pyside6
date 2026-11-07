import logging
import sys
from logging.handlers import RotatingFileHandler

from .paths import LOG_DIR


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("app")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh = RotatingFileHandler(
        LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    if sys.stderr is not None:  # exe windowed: stderr = None
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
    return logger
