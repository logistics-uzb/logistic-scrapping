from loguru import logger

def setup_logger():
    logger.add("logs/app.log", rotation="1 MB", level="INFO")
    return logger
