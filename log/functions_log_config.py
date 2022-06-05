import logging, os

LOG = logging.getLogger('functions')

log_file = os.path.join(os.path.dirname(__file__), 'functions.log')
HANDLER = logging.FileHandler(log_file, encoding='utf-8')
FORMATTER = logging.Formatter('%(asctime)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)
