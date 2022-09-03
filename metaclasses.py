from dis import Bytecode


def find_data(dicts):
    load_global = []
    load_method = []
    for func in dicts:
        if type(dicts[func]).__name__ == 'function':
            byte_code = Bytecode(dicts[func])
            for instr in byte_code:
                if instr.opname == 'LOAD_METHOD':
                    load_method.append(instr.argval)
                elif instr.opname == 'LOAD_GLOBAL':
                    load_global.append(instr.argval)
    return load_global, load_method


class ClientVerifier(type):
    def __new__(cls, name, bases, dicts):
        new_class = super(ClientVerifier, cls).__new__(cls, name, bases, dicts)
        load_global, load_method = find_data(dicts)

        if 'accept' in load_method:
            raise Exception('У класса Client не должно быть вызовов - accept для сокета')
        if 'listen' in load_method:
            raise Exception('У класса Client не должно быть вызовов - listen для сокета')
        if 'socket' not in load_global:
            raise Exception('Отсутствует создание сокета на уровне класса')
        if 'SOCK_STREAM' not in load_global and 'AF_INET' not in load_global:
            raise Exception('Класс Client должен использовать сокеты для работы по TCP')
        return new_class


class ServerVerifier(type):
    def __new__(cls, name, bases, dicts):
        new_class = super(ServerVerifier, cls).__new__(cls, name, bases, dicts)
        load_global, load_method = find_data(dicts)

        if 'connect' in load_method:
            raise Exception('У класса Server не должно быть вызовов - connect  для сокета ')

        if 'SOCK_STREAM' not in load_global and 'AF_INET' not in load_global:
            raise Exception('Класс Server должен использовать сокеты для работы по TCP')
        return new_class
