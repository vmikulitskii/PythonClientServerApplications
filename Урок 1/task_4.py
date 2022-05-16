"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

WORDS = ['разработка', 'администрирование', 'protocol', 'standard']

for word in WORDS:
    word_b = word.encode('utf-8')
    print(word_b, type(word_b))
    word_s = word_b.decode('utf-8')
    print(word_s, type(word_s))
