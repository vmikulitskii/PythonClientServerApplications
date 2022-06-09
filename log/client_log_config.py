import logging, os
import sys

LOG = logging.getLogger('client')

log_file = os.path.join(os.path.dirname(__file__), 'client.log')
HANDLER = logging.FileHandler(log_file, encoding='utf-8')

FORMATTER = logging.Formatter('%(asctime)s - %(levelname)8s - %(name)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOG.addHandler(HANDLER)

# Если надо вывод в консоль
# HANDLER_CONSOLE = logging.StreamHandler(sys.stdout)
# HANDLER_CONSOLE.setFormatter(FORMATTER)
# LOG.addHandler(HANDLER_CONSOLE)
LOG.setLevel(logging.DEBUG)
