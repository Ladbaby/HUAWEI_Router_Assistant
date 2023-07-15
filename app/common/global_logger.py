import logging
import logging.handlers as handlers
import time
import os

logger = logging.getLogger('global')
logger.setLevel(logging.DEBUG)

os.makedirs('log', exist_ok=True)

logHandler = handlers.RotatingFileHandler('log/debug.log', maxBytes=5242880, backupCount=2, encoding='utf-8')
logHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s:%(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
