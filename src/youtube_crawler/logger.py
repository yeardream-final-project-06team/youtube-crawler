import os
import logging

logger = logging.getLogger("web-crawler-container")

if os.getenv("MODE", "dev") == "prod":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)
