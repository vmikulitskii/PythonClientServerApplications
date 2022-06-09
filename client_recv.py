from socket import socket, AF_INET, SOCK_STREAM, gaierror
import datetime
import sys
import logging
import log.client_log_config
from common.decorators import log

from common.variables import *
from common.utils import get_message, send_message

LOG = logging.getLogger('client')


@log
def create_presence(akk_name):
    """
    Получает имя пользователя и генерирует presence сообщение
    :param akk_name: str
    :return: byte
    """
    msg = {
        ACTION: PRESENCE,
        TIME: datetime.datetime.now().timestamp(),
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: akk_name,
            STATUS: "Yep, I am here!"
        }
    }
    LOG.info('Cоздано PRESENCE сообщение')
    return msg


@log
def parse_response(response):
    """
    Проверяет ответ от сервера
    :param response: dict
    :return:
    """
    if response.get(RESPONSE) == 200:
        LOG.debug(f'Получен ответ от сервера -  {response[RESPONSE]}: {response[ALLERT]}')
        return f'{response[RESPONSE]}: {response[ALLERT]}'
    elif response.get(RESPONSE) == 400:
        LOG.debug(f'Получен ответ от сервера - {response[RESPONSE]}: {response[ERROR]}')
        return f'{response[RESPONSE]}: {response[ERROR]}'
    elif response.get(ACTION) == MSG:
        LOG.debug(f'Получен ответ от сервера - {response[MESSAGE]}')
        return f'{response[FROM]}:{response[MESSAGE]}'


@log
def main():
    try:
        addr = sys.argv[1]
        if '-p' in sys.argv:
            index = sys.argv.index('-p')
            port = int(sys.argv[index + 1])
        else:
            port = DEFAULT_PORT

        if '-n' in sys.argv:
            index = sys.argv.index('-n')
            akk_name = sys.argv[index + 1]
        else:
            akk_name = DEFAULT_USER

    except IndexError:
        LOG.error('Не введен ip адрес сервера')
    except OverflowError:
        LOG.error('Введен неправильный порт, порт должен быть от 0-65535')
    except ValueError:
        LOG.error('Введен неправильный порт, порт должен быть числом от 0-65535')

    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((addr, port))
            LOG.info(f'Клиент подключился к серверу {addr} порт {port}')
            send_message(client_socket, create_presence(akk_name))

            while True:
                response = get_message(client_socket)
                response = parse_response(response)
                print(response)
    except gaierror:
        LOG.error('Неправильно введен Ip адрес')
    except ConnectionRefusedError as err:
        LOG.error(err)


if __name__ == "__main__":
    main()
