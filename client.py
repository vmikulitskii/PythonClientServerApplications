import json
import time
from socket import socket, AF_INET, SOCK_STREAM, gaierror
import datetime
import sys
import logging
import log.client_log_config
from common.decorators import log
import threading

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


def message_from_server(client_sock, akk_name):
    while True:
        try:
            message = get_message(client_sock)
            if message.get(ACTION) == MSG:
                if message.get(TO) == akk_name or message.get(TO) == '#':
                    LOG.debug(f'Получено сообщение от сервера - {message[MESSAGE]}')
                    print(f'\nПолучено сообщение от {message[FROM]} - {message[MESSAGE]}')
                    print('Введите команду: ')
        except OSError:
            print(f'Потеряно соединение с сервером.')
            break


def create_message(text, akk_name, to='#'):
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
        FROM: akk_name,
        MESSAGE: text
    }
    LOG.info('Cоздано MESSAGE сообщение')
    return msg


def create_exit_message(akk_name):
    msg = {
        ACTION: EXIT,
        TIME: datetime.datetime.now().timestamp(),
        FROM: akk_name
    }
    LOG.info('Cоздано MESSAGE сообщение')


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


def user_interactive(client_socket, akk_name):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            to_user = input('Введите получателя сообщения: ')
            text = input('Введите сообщение: ')
            send_message(client_socket, create_message(text, akk_name, to_user))
            time.sleep(0.5)
        elif command == 'exit':
            send_message(client_socket, create_exit_message(akk_name))
            print('Завершение соединения.')
            LOG.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        elif command == 'help':
                print_help()
        else:
            print('Команда не распознана')


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
            response = parse_response(get_message(client_socket))
            print(response)

            receiver = threading.Thread(target=message_from_server, args=(client_socket, akk_name))
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=user_interactive, args=(client_socket, akk_name))
            user_interface.daemon = True
            user_interface.start()

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break
    except gaierror:
        LOG.error('Неправильно введен Ip адрес')
    except ConnectionRefusedError as err:
        LOG.error(err)


if __name__ == "__main__":
    main()
