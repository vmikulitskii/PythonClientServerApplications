from task_2 import host_range_ping
import tabulate


def host_range_ping_tab(first_ip, last_ip):
    result = host_range_ping(first_ip, last_ip, write_result=False)
    print(tabulate.tabulate(result, headers='keys', tablefmt='pipe'))


if __name__ == '__main__':
    host_range_ping_tab('192.168.1.36', '192.168.1.38')
