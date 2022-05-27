import unittest
from client import create_presence, parse_response
from common.variables import *


class ClientTest(unittest.TestCase):
    def test_create_presence_action(self):
        presence = create_presence()
        action = presence[ACTION]
        self.assertEqual(action, PRESENCE, 'Action != Presense')

    def test_create_presence_time(self):
        presence = create_presence()
        self.assertTrue(TIME in presence and presence[TIME] > 0, 'В сообщении отсутствует Time')

    def test_create_presence_user_name(self):
        self.user = 'Guido'
        presence = create_presence(self.user)
        self.assertEqual(presence[USER][ACCOUNT_NAME], self.user, 'Неправильное имя пользователя')

    def test_create_presence_user_default_name(self):
        self.user = 'Guest'
        presence = create_presence()
        self.assertEqual(presence[USER][ACCOUNT_NAME], self.user, 'Неправильное имя пользователя')

    def test_parse_response_200(self):
        response = parse_response({RESPONSE: 200, ALLERT: 'Приветствую вас - Guest'})
        self.assertEqual(
            response, '200: Приветствую вас - Guest')

    def test_parse_response_400(self):
        response = parse_response({RESPONSE: 400, ERROR: 'Bad Request'})
        self.assertEqual(
            response, '400: Bad Request')

    def test_no_response(self):
        self.assertRaises(KeyError, parse_response,{})


if __name__ == '__main__':
    unittest.main()
