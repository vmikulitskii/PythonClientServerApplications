import os
import subprocess
import time

server = subprocess.Popen(['python', 'server.py','-p','7777'], creationflags=subprocess.CREATE_NEW_CONSOLE)
quantity = int(input('Введите количество клиентов - '))
for i in range(quantity):
    client = subprocess.Popen(['python', 'client.py', '127.0.0.1', '-p','7777','-n', f'User-{i + 1}'],
                              creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(1)
