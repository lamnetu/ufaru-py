import sys
from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    # Убираем стандартный sink (чтобы не дублировать)
    logger.remove()

    # 1. В консоль (stderr) — для docker logs
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    # 2. В файл с ротацией — для истории
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",   # новый файл каждый день
        retention="14 days",# хранить 14 дней
        compression="zip",  # старые сжимать
        level="DEBUG",      # в файл пишем подробнее
        enqueue=True,       # безопасно для async/multiprocessing
    )