import subprocess
import chardet
import ipaddress
import socket


def host_ping(ip_list, n=1, write_result=True):
    ip_ping_result = []
    for ip in ip_list:
        ip = socket.gethostbyname(ip)
        ip = ipaddress.ip_address(ip)
        PROC = subprocess.Popen(['ping', '-n', str(n), ip.compressed], shell=True, stdout=subprocess.PIPE)
        data = PROC.stdout.read()
        result = chardet.detect(data)
        out = data.decode(result['encoding'])
        if 'узел недоступен' in out:
            ip_ping_result.append({'Узел недоступен': ip})
        else:
            ip_ping_result.append({'Узел доступен': ip})
        if write_result:
            print(f'{list(ip_ping_result[-1].values())[0]} - {list(ip_ping_result[-1].keys())[0]}')

    return ip_ping_result


if __name__ == '__main__':
    list_ip = ['yandex.ru', '192.168.1.200']
    host_ping(list_ip)
