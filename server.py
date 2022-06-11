import select
import time
from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys
import logging
import log.server_log_config
from common.decorators import log

from common.utils import get_message, send_message
from common.variables import *

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
    elif ACTION in message and message[
        ACTION] == MSG and TIME in message and FROM in message and TO in message and message[TO] == '#':
        answer = message
    else:
        answer = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
    LOG.debug(f'Сформирован ответ: {answer}')
    return answer


def read_requests(read_clients, all_clients: list):
    """
    Принимаем список клиентов на чтение и общий список клиентов
    Возвращаем словарь клиент - запрос
    :param read_clients:
    :param all_clients:
    :return:
    """
    responses = {}

    for sock in read_clients:
        try:
            data = get_message(sock)
            responses[sock] = data
        except:
            LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
            all_clients.remove(sock)
    return responses


def write_responses(requests, write_clients, all_clients):
    """
    Получаем словарь с запросами, список клиентов на запись и всех клиентов
    если в сообщение есть TO = # то это сообщение будет отправлено всем клиентам
    если это презенс сообщение, то оно будет обработано и ответ прийдет только тому клиенту,э
    который его отправил

    :param requests:
    :param write_clients:
    :param all_clients:
    :return:
    """
    for sock in write_clients:
        try:
            for key in requests:
                resp = requests[key]
                if requests[key].get(TO) == "#":
                    send_message(sock, create_answer(resp))
                elif requests[key].get(ACTION) == PRESENCE:
                    if key == sock:
                        send_message(sock, create_answer(resp))
        except Exception as E:
            LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
            print(E)
            sock.close
            all_clients.remove(sock)


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
        serv_socket.settimeout(0.5)
        clients = []

        LOG.info(f'Сервер запущен на порту {port}')
        while True:
            try:
                client_sock, client_addr = serv_socket.accept()
                LOG.info(f'Подключился ПК {client_addr}')
            except OSError:
                pass
            else:
                clients.append(client_sock)
            # data = get_message(client_sock)
            # answer = create_answer(data)
            # send_message(client_sock, answer)
            # client_sock.close()
            # LOG.info(f'закрыто соединение с ПК {client_addr}')
            finally:
                wait = 10
                read = []
                write = []
                try:
                    read, write, error = select.select(clients, clients, [], wait)
                except:
                    pass

                responses = read_requests(read, clients)
                write_responses(responses, write, clients)
                pass

    except OverflowError:
        LOG.error('Введен неправильный порт, порт должен быть от 0-65535')
    except ValueError:
        LOG.error('Введен неправильный порт, порт должен быть числом от 0-65535')


if __name__ == "__main__":
    main()
