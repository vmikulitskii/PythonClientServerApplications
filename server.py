from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys
import logging
import log.server_log_config
from common.decorators import log

from common.utils import get_message, send_message
from common.variables import ACTION, TIME, USER, PRESENCE, ERROR, RESPONSE, ALLERT, MAX_CONNECTIONS, DEFAULT_PORT, \
    ACCOUNT_NAME

LOG = logging.getLogger('server')


@log
def create_answer(message):
    """
    Функция принимает сообщение в виде словаря, проверяет его и генерирует ответ
    :param message: dict
    :return: dict
    """
    LOG.debug(f'Получено сообщение: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        answer = {
            RESPONSE: 200,
            TIME: datetime.datetime.now().timestamp(),
            ALLERT: f'Приветствую вас - {message[USER][ACCOUNT_NAME]}'
        }
    else:
        answer = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
    LOG.debug(f'Сформирован ответ: {answer}')
    return answer


@log
def main():
    serv_socket = socket(AF_INET, SOCK_STREAM)
    try:

        if '-p' in sys.argv:
            index = sys.argv.index('-p')
            port = int(sys.argv[index + 1])
        else:
            port = DEFAULT_PORT
        if '-a' in sys.argv:
            index = sys.argv.index('-a')
            addr = sys.argv[index + 1]
        else:
            addr = ''

        serv_socket.bind((addr, port))
        serv_socket.listen(MAX_CONNECTIONS)

        try:
            LOG.info(f'Сервер запущен на порту {port}')
            while True:
                client_sock, client_addr = serv_socket.accept()
                LOG.info(f'Подключился ПК {client_addr}')
                data = get_message(client_sock)
                answer = create_answer(data)
                send_message(client_sock, answer)
                client_sock.close()
                LOG.info(f'закрыто соединение с ПК {client_addr}')
        finally:
            serv_socket.close()
    except OverflowError:
        LOG.error('Введен неправильный порт, порт должен быть от 0-65535')
    except ValueError:
        LOG.error('Введен неправильный порт, порт должен быть числом от 0-65535')


if __name__ == "__main__":
    main()
