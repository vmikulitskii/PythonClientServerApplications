import logging, os
import sys

import log.functions_log_config
import traceback


def log(func):
    def wrapper(*args, **kwargs):
        LOG = logging.getLogger('functions')
        parent = traceback.extract_stack()[-2].name
        file = traceback.extract_stack()[-2].filename
        text = 'функции ' if parent != '<module>' else ''
        if args or kwargs:
            LOG.debug(f'Функция {func.__name__} с аргументами {args, kwargs} вызвана из {text}{parent} {file} ')
        else:
            LOG.debug(f'Функция {func.__name__} вызвана из {text}{parent} {file} ')
        res = func(*args, **kwargs)
        return res

    return wrapper


def login_required(func):
    def wrapper(self):
        if self.authorized:
            return func(self)
        else:
            print(f'Для запуска функции {func.__name__} необходима авторизация на сервере')

    return wrapper
