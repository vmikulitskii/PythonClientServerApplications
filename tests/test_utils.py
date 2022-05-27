import json
import unittest
from common.utils import get_message, send_message
from common.variables import *


class TestSocket():
    def __init__(self, dict):
        self.test_dict = dict

    def recv(self, max_package_lenght):
        recv_msg = json.dumps(self.test_dict).encode(ENCODING)
        return recv_msg

    def send(self, encode_json_message):
        self.send_msg = encode_json_message


class UtilTests(unittest.TestCase):
    test_send_msg = {
        ACTION: PRESENCE,
        TIME: '5.5',
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: 'Guest',
            STATUS: "Yep, I am here!"
        }
    }

    test_recv_msg_ok = {
        RESPONSE: 200,
        TIME: '5.5',
        ALLERT: f'Приветствую вас - Guest'
    }

    test_recv_msg_bad = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_get_message(self):
        test_cock = TestSocket(self.test_send_msg)

        self.assertEqual(get_message(test_cock), self.test_send_msg, 'Сообщение не получено')

    def test_send_message_200(self):
        test_cock = TestSocket(self.test_recv_msg_ok)
        send_message(test_cock, self.test_recv_msg_ok)
        test_msg = json.dumps(self.test_recv_msg_ok).encode(ENCODING)
        self.assertEqual(test_cock.send_msg, test_msg)

    def test_send_message_400(self):
        test_cock = TestSocket(self.test_recv_msg_bad)
        send_message(test_cock, self.test_recv_msg_bad)
        test_msg = json.dumps(self.test_recv_msg_bad).encode(ENCODING)
        self.assertEqual(test_cock.send_msg, test_msg)