"""
FraudShield Structured Logging Configuration.
"""

import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> None:
    """Configures structured logging across the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly verbose third-party loggers
    for logger_name in ["uvicorn.access", "sqlalchemy.engine", "matplotlib"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


logger = logging.getLogger("FraudShield")

