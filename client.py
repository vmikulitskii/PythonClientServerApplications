from socket import socket, AF_INET, SOCK_STREAM, gaierror
import datetime
import sys
import logging
import log.client_log_config

from common.variables import DEFAULT_USER, DEFAULT_PORT, ACTION, TIME, USER, PRESENCE, ERROR, RESPONSE, ALLERT, \
    ACCOUNT_NAME, STATUS, TYPE
from common.utils import get_message, send_message

LOG = logging.getLogger('client')


def create_presence(akk_name=DEFAULT_USER):
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


def parse_response(response):
    """
    Проверяет ответ от сервера
    :param response: dict
    :return:
    """
    if response[RESPONSE] == 200:
        LOG.debug(f'Получен ответ от сервера -  {response[RESPONSE]}: {response[ALLERT]}')
        return f'{response[RESPONSE]}: {response[ALLERT]}'
    elif response[RESPONSE] == 400:
        LOG.debug(f'Получен ответ от сервера - {response[RESPONSE]}: {response[ERROR]}')
        return f'{response[RESPONSE]}: {response[ERROR]}'


def main():
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        addr = sys.argv[1]
        if '-p' in sys.argv:
            port = int(sys.argv[3])
        else:
            port = DEFAULT_PORT

        client_socket.connect((addr, port))
        LOG.info(f'Клиент подключился к серверу {addr} порт {port}')
        send_message(client_socket, create_presence())
        response = get_message(client_socket)
        response = parse_response(response)
        print(response)
        client_socket.close()
    except IndexError:
        LOG.error('Не введен ip адрес сервера')
    except OverflowError:
        LOG.error('Введен неправильный порт, порт должен быть от 0-65535')
    except ValueError:
        LOG.error('Введен неправильный порт, порт должен быть числом от 0-65535')
    except gaierror:
        LOG.error('Неправильно введен Ip адрес')
    except ConnectionRefusedError as err:
        LOG.error(err)


if __name__ == "__main__":
    main()
