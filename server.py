import select
import time
from pprint import pprint
from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys
import logging
import log.server_log_config
from common.decorators import log

from common.utils import get_message, send_message
from common.variables import *
from descriptors import CorrectPort
from metaclasses import ClientVerifier, ServerVerifier

LOG = logging.getLogger('server')


class Server(metaclass=ServerVerifier):
    port = CorrectPort()

    def __init__(self):
        if '-p' in sys.argv:
            index = sys.argv.index('-p')
            self.port = int(sys.argv[index + 1])
        else:
            self.port = DEFAULT_PORT
        if '-a' in sys.argv:
            index = sys.argv.index('-a')
            self.addr = sys.argv[index + 1]
        else:
            self.addr = ''
        self.clients = []

    @log
    def create_answer(self, message):

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
            ACTION] == MSG and TIME in message and FROM in message and TO in message:
            answer = message
        else:
            answer = {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            }
        LOG.debug(f'Сформирован ответ: {answer}')
        return answer

    def read_requests(self, read_clients, all_clients: list):
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

    def write_responses(self, requests, write_clients, all_clients):
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
                    if requests[key].get(TO):
                        send_message(sock, self.create_answer(resp))
                    elif requests[key].get(ACTION) == PRESENCE:
                        if key == sock:
                            send_message(sock, self.create_answer(resp))
                    elif requests[key].get(ACTION) == EXIT:
                        if key == sock:
                            sock.close
                            all_clients.remove(sock)
                            LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
                            return
            except Exception as E:
                LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
                print(E)
                sock.close
                all_clients.remove(sock)

    def start(self):
        serv_socket = socket(AF_INET, SOCK_STREAM)
        serv_socket.bind((self.addr, self.port))
        serv_socket.settimeout(0.5)
        serv_socket.listen(MAX_CONNECTIONS)

        LOG.info(f'Сервер запущен на порту {self.port}')

        while True:
            try:
                client_sock, client_addr = serv_socket.accept()
                LOG.info(f'Подключился ПК {client_addr}')
                print(f'Подключился ПК {client_addr}')
            except OSError:
                pass
            else:
                self.clients.append(client_sock)
            finally:
                wait = 10
                read = []
                write = []
                try:
                    read, write, error = select.select(self.clients, self.clients, [], wait)
                except:
                    pass

                responses = self.read_requests(read, self.clients)
                self.write_responses(responses, write, self.clients)


@log
def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
