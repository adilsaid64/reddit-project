import logging

def setup_logger():
    logger = logging.getLogger('RedditLogger')
    logger.setLevel(logging.DEBUG)

    # Check if the logger already has handlers
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # Optional: Set log level for this handler

        file_handler = logging.FileHandler('project.log')
        file_handler.setLevel(logging.DEBUG)  # Optional: Set log level for this handler

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
