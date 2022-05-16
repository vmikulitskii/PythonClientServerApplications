"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
import chardet, subprocess

ADDRESSES = ['yandex.ru', 'youtube.com']
for address in ADDRESSES:
    PING = subprocess.Popen(['ping', address], stdout=subprocess.PIPE)
    for line in PING.stdout:
        encoding = chardet.detect(line)['encoding']
        line = line.decode(encoding).encode('utf-8').decode('utf-8')
        print(line)
