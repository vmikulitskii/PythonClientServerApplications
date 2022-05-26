from socket import socket, AF_INET, SOCK_STREAM
import datetime
import sys, json


def main():
    serv_socket = socket(AF_INET, SOCK_STREAM)

    if '-p' in sys.argv:
        index = sys.argv.index('-p')
        port = int(sys.argv[index + 1])
    else:
        port = 7777
    if '-a' in sys.argv:
        index = sys.argv.index('-a')
        addr = sys.argv[index + 1]
    else:
        addr = ''

    serv_socket.bind((addr, port))
    serv_socket.listen(2)

    try:
        while True:
            client_sock, client_addr = serv_socket.accept()
            data = client_sock.recv(1024).decode('utf-8')
            data = json.loads(data)
            if data.get('action') == 'presence':
                user_name = data['user']['account_name']
                print(f'Подключился {user_name}')
                client_sock.send(get_presence_answer(user_name))
                client_sock.close()
    finally:
        serv_socket.close()


def get_presence_answer(user_name):
    """
    Получает имя пользователя и генерирует закодированный ответ на presence
    :param user_name: str
    :return: byte
    """
    data = {
        'response': 200,
        "time": datetime.datetime.now().timestamp(),
        "allert": f'Приветствую вас - {user_name} '
    }
    return json.dumps(data).encode('utf-8')


if __name__ == "__main__":
    main()
