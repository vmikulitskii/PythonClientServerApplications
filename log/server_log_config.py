import logging, os
import logging.handlers

LOG = logging.getLogger('server')

log_file = os.path.join(os.path.dirname(__file__), 'server.log')
HANDLER = logging.handlers.TimedRotatingFileHandler(log_file, encoding='utf-8', interval=1, when='D')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)
