"""Константы"""

# Порт по умолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
ALLERT = 'allert'
STATUS = 'status'
TYPE = 'type'
MSG = 'msg'
FROM = 'from'
MESSAGE = 'message'
TO = 'to'
EXIT = 'exit'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
GET_CONTACTS = "get_contacts"
# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'

SENT ='sent'
RECEIVED ='received'

# Имя пользователя по умолчанию
DEFAULT_USER = 'Guest'

__all__ = ('DEFAULT_PORT', 'DEFAULT_IP_ADDRESS', 'MAX_CONNECTIONS',
           'MAX_PACKAGE_LENGTH', 'ENCODING', 'ACTION', 'TIME', 'USER', 'ACCOUNT_NAME',
           'ALLERT', 'STATUS', 'TYPE', 'PRESENCE', 'RESPONSE', 'ERROR',
           'DEFAULT_USER','MSG','TO','FROM','MESSAGE','EXIT')
