import binascii
import hashlib
import json, sys

from common.decorators import log
from common.variables import MAX_PACKAGE_LENGTH, ENCODING


@log
def get_message(client):
    """
    Функция для получения сообщения и декодирования из байтов в словарь. Если приянто что то другое то выдает ошибку
    :param client:
    :return:
    """
    data = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(data, bytes):
        data_dict = json.loads(data.decode(ENCODING))
        if isinstance(data_dict, dict):
            return data_dict
        else:
            return ValueError
    else:
        return ValueError


@log
def send_message(sock, message):
    """
    Функция принимает сокет и словарь, кодирует его и отправляет
    :param sock:
    :param message:dict
    :return:
    """

    if isinstance(message, dict):
        json_message = json.dumps(message).encode(ENCODING)
        sock.send(json_message)
    else:
        return ValueError


def cripto_pass(passwrd):
    passwrd = passwrd.encode(encoding='utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', passwrd, b'salt for the dishwasher 303', 100000)
    new_pass = binascii.hexlify(dk)
    print(new_pass)
    return new_pass
