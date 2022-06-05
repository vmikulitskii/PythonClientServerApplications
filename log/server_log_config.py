import logging
import logging.handlers

LOG = logging.getLogger('server')

HANDLER = logging.handlers.TimedRotatingFileHandler('log/server.log', encoding='utf-8', interval=1, when='D')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)
