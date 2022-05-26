import json
from socket import socket, AF_INET, SOCK_STREAM, gaierror
import datetime
import sys


def get_presence(akk_name):
    """
    Получает имя пользователя и генерирует presence сообщение
    :param akk_name: str
    :return: byte
    """
    msg = {
        "action": "presence",
        "time": datetime.datetime.now().timestamp(),
        "type": "status",
        "user": {
            "account_name": akk_name,
            "status": "Yep, I am here!"
        }
    }
    return json.dumps(msg).encode('utf-8')


def main():
    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        addr = sys.argv[1]
        if '-p' in sys.argv:
            port = int(sys.argv[3])
        else:
            port = 7777

        client_socket.connect((addr, port))
        client_socket.send(get_presence('Vladimir_M'))
        data = client_socket.recv(1024).decode('utf-8')
        data = json.loads(data)
        if data.get('response') == 200:
            print(data['allert'])
        client_socket.close()
    except IndexError:
        print('Необходимо ввести ip адрес сервера')
    except OverflowError:
        print('Порт должен быть от 0-65535')
    except ValueError:
        print('Порт это число от 0-65535')
    except gaierror:
        print('Неправильно введен Ip адрес')



if __name__ == "__main__":
    main()
