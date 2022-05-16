import chardet

"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""

WORDS = ["attribute", "класс", "функция", "type"]

"""Вариант 1"""


def checking_for_сyrillic(text):
    kirill = ('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    for letter in text.lower():
        if letter in kirill:
            return True
    return False


for word in WORDS:
    if checking_for_сyrillic(word):
        print(f'слово {word} - невозможно записать в байтовом типе с помощью маркировки b''(без encode decode)')
    else:
        print(f'слово {word} - можно записать в байтовом типе с помощью маркировки b'' ')

"""Вариант с исключением"""
print('--------------------------------')

for word in WORDS:
    try:
        word_b = bytes(word, 'ascii')
        print(f'слово {word} можно записать в байтовом типе с помощью маркировки b'' ')
    except UnicodeEncodeError:
        print(f'слово {word} - невозможно записать в байтовом типе с помощью маркировки b''(без encode decode)')
