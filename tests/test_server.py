import unittest
from server import create_answer
from common.variables import *


class Tests(unittest.TestCase):
    message = {
        ACTION: PRESENCE,
        TIME: '5.5',
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: 'Guest',
            STATUS: "Yep, I am here!"
        }
    }

    def test_create_answer_200(self):
        answer = create_answer(self.message)
        answer[TIME] = '5.5'
        self.assertEqual(answer, {RESPONSE: 200, TIME: '5.5', ALLERT: 'Приветствую вас - Guest'})

    def test_create_answer_400(self):
        answer = create_answer({})
        self.assertEqual(answer, {RESPONSE: 400,ERROR: 'Bad Request'})

