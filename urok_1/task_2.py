
from task_1 import host_ping


def host_range_ping(first_ip, last_ip,write_result=True):
    host_list = []
    ip_baza = '.'.join(str.split(first_ip, '.')[:3])
    first_ip_last_octet = int(str.split(first_ip, '.')[3])
    last_ip_last_octet = int(str.split(last_ip, '.')[3])
    for numb in range(first_ip_last_octet, last_ip_last_octet + 1):
        host_list.append(f'{ip_baza}.{numb}')
    result = host_ping(host_list,write_result=write_result)

    return result


if __name__ == '__main__':
    host_range_ping('192.168.1.36', '192.168.1.38')
