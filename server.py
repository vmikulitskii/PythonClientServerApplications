from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys

from common.utils import get_message, send_message
from common.variables import ACTION, TIME, USER, PRESENCE, ERROR, RESPONSE, ALLERT, MAX_CONNECTIONS, DEFAULT_PORT,ACCOUNT_NAME


def create_answer(message):
    """
    Функция принимает сообщение в виде словаря, проверяет его и генерирует ответ
    :param message: dict
    :return: dict
    """
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
    print(answer)
    return answer


def main():
    serv_socket = socket(AF_INET, SOCK_STREAM)

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
        while True:
            client_sock, client_addr = serv_socket.accept()
            print(f'Подключился {client_addr}')
            data = get_message(client_sock)
            print(data)
            answer = create_answer(data)
            send_message(client_sock, answer)
            client_sock.close()
    finally:
        serv_socket.close()


if __name__ == "__main__":
    main()
