import logging, os
import log.functions_log_config
import traceback


def log(func):
    def wrapper(*args, **kwargs):
        LOG = logging.getLogger('functions')
        parent = traceback.extract_stack()[-2].name
        file = traceback.extract_stack()[-2].filename
        if parent != '<module>':
            LOG.debug(f'Функция {func.__name__} вызвана из функции {parent} {file} ')
        else:
            LOG.debug(f'Функция {func.__name__} вызвана из {parent} {file} ')
        res = func(*args, **kwargs)
        return res

    return wrapper
