class CorrectPort:
    def __set_name__(self, owner, port):
        self.port = port

    def __get__(self, instance, owner):
        return instance.__dict__[self.port]

    def __set__(self, instance, value):
        if value < 1024 or value > 65535:
            raise ValueError('Порт должен быть в диапазоне от 1025 до 65535 ')
        else:
            instance.__dict__[self.port] = value
