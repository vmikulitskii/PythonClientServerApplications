import logging

LOG = logging.getLogger('client')

HANDLER = logging.FileHandler('log/client.log', encoding='utf-8')
FORMATTER = logging.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOG.addHandler(HANDLER)
LOG.setLevel(logging.DEBUG)
