import logging
from colorlog import ColoredFormatter

logger = logging.getLogger("app_logs")
logger.setLevel(logging.DEBUG)

formatter = ColoredFormatter(
    "%(log_color)s[%(levelname)s] %(asctime)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# Вивід в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Вивід у файл
file_handler = logging.FileHandler("app_logs.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))

# Додати хендлери
logger.addHandler(console_handler)
logger.addHandler(file_handler)