import logging
import time

LOG_FORMAT = "[%(asctime)s, %(levelname)s],"
LOG_FORMAT += "[%(filename)s, %(funcName)s, %(lineno)s]: %(message)s"
logger = logging
logging.Formatter.converter = time.gmtime
# logger.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logger.basicConfig(format=LOG_FORMAT, level=logging.ERROR)
