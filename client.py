""" Модуль клиента мессенджера"""
import datetime
import hashlib
import hmac
import json
import logging
import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, gaierror, socket

from Crypto.PublicKey import RSA
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt, pyqtSignal, pyqtSlot

import log.client_log_config
from client_gui import ArrivedMessage, LoginPass, MyWindow, NewLocalContact
from client_storage import ClientStorage
from common.decorators import log, login_required
from common.utils import cripto_pass, get_message, send_message
from common.variables import *
from common.variables import (ADD_CONTACT, DEL_CONTACT, GET_CONTACTS, RECEIVED,
                              SENT)
from descriptors import CorrectPort
from metaclasses import ClientVerifier, ServerVerifier

LOG = logging.getLogger('client')


class Client(QObject):
    """ Основной класс клиентской части приложения"""
    port = CorrectPort()
    message_arrived = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        try:
            # self.addr = sys.argv[1]
            self.addr = '127.0.0.1'

            if '-p' in sys.argv:
                index = sys.argv.index('-p')
                self.port = int(sys.argv[index + 1])
            else:
                self.port = DEFAULT_PORT

            if '-n' in sys.argv:
                index = sys.argv.index('-n')
                self.akk_name = sys.argv[index + 1]
            else:
                self.akk_name = DEFAULT_USER
                self.akk_name = 'User-1'

        except IndexError:
            LOG.error('Не введен ip адрес сервера')

        self.client_db = None
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = None
        self.dialog = ArrivedMessage()
        self.new_local_contact = NewLocalContact()
        self.login_pass = LoginPass()
        self.client_socket = None
        self.passwrd = ''
        self.authorized = False

    @log
    def create_presence(self):
        """
        Получает имя пользователя и генерирует presence сообщение

        :return: byte
        """
        msg = {
            ACTION: PRESENCE,
            TIME: datetime.datetime.now().timestamp(),
            TYPE: STATUS,
            USER: {
                ACCOUNT_NAME: self.akk_name,
                STATUS: "Yep, I am here!"
            }
        }
        LOG.info('Cоздано PRESENCE сообщение')
        return msg

    @log
    def parse_response(self, response):
        """
        Проверяет ответ от сервера
        :param response: dict
        :return:
        """
        if response.get(RESPONSE) == 200:
            LOG.debug(
                f'Получен ответ от сервера -  {response[RESPONSE]}: {response[ALLERT]}')
            return response[RESPONSE], response[ALLERT]
        elif response.get(RESPONSE) == 400:
            LOG.debug(
                f'Получен ответ от сервера - {response[RESPONSE]}: {response[ERROR]}')
            return response[RESPONSE], response[ERROR]

    def message_from_server(self, client_sock):
        while True:
            try:
                message = get_message(client_sock)
                if message.get(ACTION) == MSG:
                    if message.get(
                            TO) == self.akk_name or message.get(TO) == '#':
                        LOG.debug(
                            f'Получено сообщение от сервера - {message[MESSAGE]}')
                        print(
                            f'\nПолучено сообщение от {message[FROM]} - {message[MESSAGE]}')
                        self.client_db.add_message(
                            message[FROM], message[MESSAGE], RECEIVED)
                        print('Введите команду: ')
                        self.message_arrived.emit(message[FROM])

                elif message.get(RESPONSE) == 201:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(f'\nНовый контакт добавлен на сервере')
                elif message.get(RESPONSE) == 202:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    contacts = message.get(ALLERT)
                    if contacts:
                        print(f'Ваш список контактов:')
                        for contact in contacts:
                            print(contact)
                    else:
                        print('Ваш список контактов пуст')

                elif message.get(RESPONSE) == 203:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(f'\nПользователь удалён из серверного контакт листа')

                elif message.get(RESPONSE) == 205:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(f'\n{message.get(ALLERT)}')

                elif message.get(RESPONSE) == 401:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(
                        f'\nПользователь с таким именем не зарегистрирован на сервере')

                elif message.get(RESPONSE) == 402:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(f'\nПользователь с таким именем уже в вашем контакт листе')

                elif message.get(RESPONSE) == 403:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(
                        f'\nПользователь с таким именем отсутствует в вашем контакт листе')

                elif message.get(RESPONSE) == 405:
                    LOG.debug(
                        f'Получено сообщение от сервера - {message[RESPONSE]}')
                    print(f'\n{message.get(ERROR)}')

            except OSError:
                print(f'Потеряно соединение с сервером.')
                break

    def create_message(self, text, to):
        """
        Получает текст имя отправителя и получателя и генерирует message
        :param text: str
        :param akk_name: str
        :param to: str
        :return: dict
        """
        msg = {
            ACTION: MSG,
            TIME: datetime.datetime.now().timestamp(),
            TO: to,
            FROM: self.akk_name,
            MESSAGE: text
        }
        LOG.info('Cоздано MESSAGE сообщение')
        return msg

    def create_exit_message(self):
        """ Создает сообщение о выходе клиента из месседжера"""
        msg = {
            ACTION: EXIT,
            TIME: datetime.datetime.now().timestamp(),
            FROM: self.akk_name
        }
        LOG.info('Cоздано  EXIT MESSAGE сообщение')
        return msg

    def add_contact(self, new_contact):
        """
        Создает запрос серверу на добавление нового контакта
        :param new_contact: str
        :return: str
        """

        msg = {
            ACTION: ADD_CONTACT,
            TIME: datetime.datetime.now().timestamp(),
            FROM: self.akk_name,
            USER: new_contact
        }
        self.client_db.add_contact(new_contact)
        LOG.info('Cоздано add_contact сообщение')
        return msg

    def del_contact(self, contact):
        """
        Создает запрос серверу на удаление ко контакта
        :param new_contact: str
        :return: str
        """
        msg = {
            ACTION: DEL_CONTACT,
            TIME: datetime.datetime.now().timestamp(),
            FROM: self.akk_name,
            USER: contact
        }
        LOG.info('Cоздано dell_contact сообщение')
        return msg

    def get_contacts(self):
        """
        Создает запрос серверу на на получение списка контактов
        :return:
        """
        msg = {
            ACTION: GET_CONTACTS,
            TIME: datetime.datetime.now().timestamp(),
            FROM: self.akk_name
        }
        LOG.info('Cоздано get_contacts сообщение')
        return msg

    @staticmethod
    def print_help():
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение.')
        print('add contact - добавить новый контакт')
        print('del contact - удалить пользователя из контакт листа')
        print('get contacts - запросить контакт лист')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    # больше не используется
    # def user_interactive(self, client_socket):
    #     self.print_help()
    #     while True:
    #         command = input('Введите команду: ')
    #         if command == 'message':
    #             to_user = input('Введите получателя сообщения: ')
    #             text = input('Введите сообщение: ')
    #             send_message(client_socket, self.create_message(text, to_user))
    #             self.client_db.add_message(to_user, text, SENT)
    #             time.sleep(0.5)
    #         elif command == 'exit':
    #             send_message(client_socket, self.create_exit_message())
    #             print('Завершение соединения.')
    #             LOG.info('Завершение работы по команде пользователя.')
    #             time.sleep(0.5)
    #             break
    #         elif command == 'help':
    #             self.print_help()
    #         elif command == 'add contact':
    #             name = input('Введите имя пользователя:')
    #             send_message(client_socket, self.add_contact(name))
    #             time.sleep(0.5)
    #         elif command == 'del contact':
    #             name = input('Введите имя пользователя:')
    #             send_message(client_socket, self.del_contact(name))
    #             self.client_db.del_contact(name)
    #             time.sleep(0.5)
    #         elif command == 'get contacts':
    #             send_message(client_socket, self.get_contacts())
    #             time.sleep(0.5)
    #         else:
    #             print('Команда не распознана')

    # def start_window(self):
    #     app = QtWidgets.QApplication(sys.argv)
    #     self.window = MyWindow(self.client_db)
    #     self.window.view_contacts()
    #
    #     self.window.make_connection(self.window.listContacts)
    #     self.window.show()
    #     self.window.sendButton.clicked.connect(
    #         lambda: self.send_new_message(self.client_socket)
    #     )
    #     sys.exit(app.exec_())

    def send_new_message(self, client_socket):
        """
        получает сокет, берет текст из поля отправки и отправляет его
        добавляет сообщене в локальную базу и загружает в окно сообщений
        :param client_socket:
        :return:
        """
        to_user = self.window.activ_contact_name
        text = self.window.textSendEdit.toPlainText()
        self.window.textSendEdit.clear()
        send_message(client_socket, self.create_message(text, to_user))
        self.client_db.add_message(to_user, text, SENT)
        self.window.load_last_history(to_user)
        time.sleep(0.5)

    @pyqtSlot(str)
    def new_message_allert(self, user_name):
        """
        Срабатывает при получении нового сообщения. Проверяет, открыт ли чат с этим
        пользователем. Если да, то просто подгружает сообщения. Если нет то выдает
        окно с предложением перейти в чат с этим контактом.
        :param user_name: str
        :return:
        """
        if self.window.activ_contact_name == user_name:
            self.window.load_last_history(user_name)
        else:
            self.dialog.userNamelabel.setText(user_name)
            self.dialog.show()
            self.dialog.buttonBox.accepted.connect(
                lambda: self.select_chat(user_name))

    def select_chat(self, user_name):
        """
        Загружает сообщения с пользователем, и делает его активным
        что бы дальнейшие сообщения отправлялись ему
        :param user_name: str
        :return:
        """
        self.window.load_last_history(user_name)
        self.window.activ_contact_name = user_name

    def add_new_local_contact(self):
        """Добавляет новый контакт в локальную базу"""
        user_name = self.new_local_contact.userNameEdit.text()
        self.client_db.add_contact(user_name)
        self.window.listContacts.clear()
        self.window.view_contacts()

    def authorization(self):
        """
        Получаем логин и пароль из полей окна, хешируем пароль
        Отправляем presence. Если получаем в ответ 407 то значит такой пользователь
        не зарегистрирован на сервере. Если получаем 210 то получаем message хешируем его
        с помошью нашего пароля и отправляем на вервер. Если получаем 200 значит всё ок.
        ставим флаг что мы авторизованы и закрываем окно. Если получаем 408 то выводим
        сообщение что пароль не верен.

        :return:
        """

        self.akk_name = self.login_pass.loginEdit.text()
        passwrd = cripto_pass(self.login_pass.passEdit.text())
        send_message(self.client_socket, self.create_presence())
        answer = get_message(self.client_socket)
        if answer[RESPONSE] == 407:
            self.login_pass.messageLabel.setText(answer[ERROR])
            self.login_pass.edit_clear()
        elif answer[RESPONSE] == 400:
            self.login_pass.messageLabel.setText(answer[ERROR])
            self.login_pass.edit_clear()
        elif answer[RESPONSE] == 210:
            message = self.client_socket.recv(32)
            hash = hmac.new(passwrd, message, digestmod=hashlib.sha3_256)
            digest = hash.digest()
            self.client_socket.send(digest)
            answer = get_message(self.client_socket)
            if answer[RESPONSE] == 200:
                print(answer[ALLERT])
                self.authorized = True
                self.client_db = ClientStorage(self.akk_name)
                self.login_pass.close()
            elif answer[RESPONSE] == 408:
                self.login_pass.messageLabel.setText(answer[ERROR])
                self.login_pass.passEdit.clear()

    def login(self):
        """
        Запускаем окно Логин-Пароль. Подключаемся к серверу. Ждем ввода логина, пароля и нажания кнопки.

        Позже надо сделать тут проверки на допустимый логин и пароль
        :return:
        """
        self.login_pass.show()
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((self.addr, self.port))
        self.client_socket = client_socket
        LOG.info(f'Клиент подключился к серверу {self.addr} порт {self.port}')
        print(f'Клиент подключился к серверу {self.addr} порт {self.port}')
        self.login_pass.enterButton.clicked.connect(self.authorization)
        self.app.exec_()

    def send_public_key(self):
        """
        Функция отправки публичного ключа на сервер.
        :return:
        """
        msg = {
            ACTION: PUBLIC_KEY,
            TIME: datetime.datetime.now().timestamp(),
            USER: {
                ACCOUNT_NAME: self.akk_name,
            },
            KEY: self.public_key.decode()
        }
        send_message(self.client_socket, msg)
        answer = get_message(self.client_socket)
        if answer[RESPONSE] == 203:
            print(answer[ALLERT])
        else:
            print('Что то пошло не так')

    @login_required
    def start(self):
        """
        Запуск основного окна программы, происходит только если
        пользователь авторизовался на сервере.
        :return:
        """
        try:
            print('start')

            self.window = MyWindow(self.client_db)

            receiver = threading.Thread(
                target=self.message_from_server, args=(
                    self.client_socket,))
            receiver.daemon = True
            receiver.start()

            self.window.view_contacts()
            self.window.make_connection(self.window.listContacts)
            self.window.show()
            self.window.sendButton.clicked.connect(
                lambda: self.send_new_message(self.client_socket)
            )
            self.window.actionNewContact.triggered.connect(
                self.new_local_contact.show)
            self.message_arrived.connect(self.new_message_allert)
            self.new_local_contact.buttonBox.accepted.connect(
                self.add_new_local_contact)

            sys.exit(self.app.exec_())
        except gaierror:
            LOG.error('Неправильно введен Ip адрес')
        except ConnectionRefusedError as err:
            LOG.error(err)


def generate_key():
    """
    Генерация ключей для сквозного шифрования
    :return:
    """
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return private_key, public_key


def main():
    ''' Создает обьект клиента, запускает функцию авторизации. Проверяет сгенерированы ли ключи
    если нет то генерирует, отправляет публичный ключ на сервер'''
    client = Client()
    client.login()
    keys = client.client_db.get_keys()
    if keys:
        client.private_key = keys.private_key
        client.public_key = keys.public_key
    else:
        client.private_key, client.public_key = generate_key()
        client.client_db.add_keys(client.private_key, client.public_key)
    client.send_public_key()

    client.start()


if __name__ == "__main__":
    main()
