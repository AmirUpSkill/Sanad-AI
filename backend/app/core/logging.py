from __future__ import annotations 

import logging 
import sys 

from loguru import logger 

from app.core.config import Settings 

class _InterceptHandler(logging.Handler):
    """ 
        Update standard logging (uvicorn/fastapi/sqlalchemy logs) inot loguru.
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)
        frame, depth = logging.currentframe(),2 
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth +=1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
    
def configure_logging(settings: Settings) -> None:
    """
    Configure loguru + intercept stdlib logging.
    Call once at startup.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.upper(),
        backtrace=not settings.is_production,
        diagnose=not settings.is_production,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
    )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    # --- Make sure uvicorn loggers propagate to root (intercepted) --- 
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    # --- Optional: reduce noisy SQL logs unless debugging --- 
    if not settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)