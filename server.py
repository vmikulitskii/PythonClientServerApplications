import configparser
import select
import time
from pprint import pprint
from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys
import logging

import PyQt5.QtCore

import log.server_log_config
from common.decorators import log

from common.utils import get_message, send_message
from common.variables import *
from common.variables import ADD_CONTACT, DEL_CONTACT, GET_CONTACTS
from descriptors import CorrectPort
from metaclasses import ClientVerifier, ServerVerifier
from server_storage import ServerStorage
from server_gui import MyWindow, UserHistory, ServerSettings
import threading
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog

LOG = logging.getLogger('server')


class Server(threading.Thread, metaclass=ServerVerifier):
    port = CorrectPort()

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        config = configparser.ConfigParser()
        config.read('server_config.ini')

        if '-p' in sys.argv:
            index = sys.argv.index('-p')
            self.port = int(sys.argv[index + 1])
        else:
            self.port = int(config['SETTINGS']['default_port'])
        if '-a' in sys.argv:
            index = sys.argv.index('-a')
            self.addr = sys.argv[index + 1]
        else:
            self.addr = config['SETTINGS']['listen_address']

        self.clients = []
        self.server_db = ServerStorage()

        self.clients_dict = {}

        self.reload = False

    @log
    def create_answer(self, message):

        """
        Функция принимает сообщение в виде словаря, проверяет его и генерирует ответ
        :param message: dict
        :return: dict
        """
        LOG.debug(f'Получено сообщение: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            user_name = message[USER][ACCOUNT_NAME]
            answer = {
                RESPONSE: 200,
                TIME: datetime.datetime.now().timestamp(),
                ALLERT: f'Приветствую вас - {user_name}'
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
                self.server_db.delete_active_user(self.clients_dict[sock])
                self.reload = True
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
                    request = requests[key]
                    if request.get(ACTION) == MSG:
                        recipient = request.get(TO)
                        sender = request.get(FROM)
                        if recipient and (self.clients_dict.get(sock) == recipient or recipient == '#'):
                            send_message(sock, self.create_answer(request))

                        elif sender and self.clients_dict.get(sock) == sender:
                            if recipient in self.clients_dict.values():
                                answer = {
                                    RESPONSE: 205,
                                    ALLERT: 'Сообщение отправлено'
                                }
                            else:
                                answer = {
                                    RESPONSE: 405,
                                    ERROR: 'Сообщение не отправлено. Клиент с таким ником не подключен к серверу'
                                }
                            send_message(sock, answer)

                    elif request.get(ACTION) == PRESENCE:
                        if key == sock:
                            user_name = request[USER][ACCOUNT_NAME]
                            if self.server_db.get_active_users(user_name):
                                answer = {
                                    RESPONSE: 400,
                                    ERROR: 'Клиент с таким ником уже подключился к серверу'
                                }
                                sock.close
                                all_clients.remove(sock)
                                send_message(sock, answer)
                                return
                            else:
                                self.clients_dict.update({sock: user_name})
                                user_ip, user_port = sock.getpeername()
                                self.server_db.user_login(user_name, user_ip, user_port)
                                self.reload = True
                            send_message(sock, self.create_answer(request))
                    elif request.get(ACTION) == EXIT:
                        if key == sock:
                            all_clients.remove(sock)
                            sock.close
                            self.server_db.delete_active_user(request[FROM])
                            LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
                            self.reload = True
                            return
                    elif request.get(ACTION) == ADD_CONTACT:
                        if key == sock:
                            result = self.server_db.add_new_contact(request[FROM],request[USER])
                            answer = {
                                RESPONSE: result
                            }
                            send_message(sock, answer)
                    elif request.get(ACTION) == DEL_CONTACT:
                        if key == sock:
                            result = self.server_db.delete_new_contact(request[FROM],request[USER])
                            answer = {
                                RESPONSE: result
                            }
                            send_message(sock, answer)
                    elif request.get(ACTION) == GET_CONTACTS:
                        if key == sock:
                            result = self.server_db.get_contacts(request[FROM])
                            answer = {
                                RESPONSE: 202,
                                ALLERT:result
                            }
                            send_message(sock, answer)
            except Exception as E:
                LOG.debug(f'Клиент{sock.fileno()} {sock.getpeername()} отключился')
                print(E)
                sock.close
                all_clients.remove(sock)
                self.server_db.delete_active_user(self.clients_dict[sock])
                self.reload = True

    def reload_active_users(self, window, history_window):
        if self.reload:
            window.active_users_table.setModel(window.get_active_users_model(self.server_db))
            window.active_users_table.resizeColumnsToContents()
            history_window.users_history_table.setModel(history_window.get_users_history_model(self.server_db))
            history_window.users_history_table.resizeColumnsToContents()
            print('Данные обновлены')
            self.reload = False

    def run(self):
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
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.active_users_table.setModel(window.get_active_users_model(server.server_db))
    window.active_users_table.resizeColumnsToContents()
    window.show()

    history_window = UserHistory()
    window.users_history.triggered.connect(history_window.show)
    history_window.users_history_table.setModel(history_window.get_users_history_model(server.server_db))
    history_window.users_history_table.resizeColumnsToContents()

    window.reload.triggered.connect(lambda: server.reload_active_users(window, history_window))

    setting_window = ServerSettings()
    window.server_settings.triggered.connect(setting_window.show)

    timer = PyQt5.QtCore.QTimer()
    timer.timeout.connect(lambda: server.reload_active_users(window, history_window))
    timer.start(1000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
