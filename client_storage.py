from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from datetime import datetime
from datetime import timedelta

Base = declarative_base()


class ClientStorage():
    class Contact(Base):
        __tablename__ = 'Contacts'
        id = Column(Integer, primary_key=True)
        name = Column(String)

        def __init__(self, name):
            self.name = name
            self.id = None

        def __repr__(self):
            return f'{self.id} - {self.name}'

    class MyKey(Base):
        __tablename__ = 'Keys'
        id = Column(Integer, primary_key=True)
        private_key = Column(String)
        public_key = Column(String)

        def __init__(self, private_key,public_key):
            self.private_key = private_key
            self.public_key = public_key

        def __repr__(self):
            return f'{self.private_key} - {self.public_key}'

    class Message(Base):
        __tablename__ = 'Messages'
        id = Column(Integer, primary_key=True)
        contact_id = Column(Integer, ForeignKey('Contacts.id'))
        text = Column(String)
        status = Column(String)
        date_time = Column(DateTime)

        Contact = relationship('Contact', back_populates='Messages')

        def __init__(self, contact_id, text, status):
            self.id = None
            self.contact_id = contact_id
            self.text = text
            self.status = status
            self.date_time = datetime.now()

        def __repr__(self):
            return f'{self.id}: {self.status} {self.contact_id} - {self.text} ({self.date_time})'

    def __init__(self, akk_name):
        """
        Получаем имя пользователя и добавляем в имя базы, что бы
        была возможность запускать несколько клиентов на одной машине
        :param akk_name:
        """
        self.akk_name = akk_name
        self.Contact.Messages = relationship('Message', back_populates="Contact")

        engine = create_engine(f'sqlite:///client_db_{self.akk_name}.db3?check_same_thread=False')
        Session = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)
        self.session = Session()

    def add_contact(self, user_name):
        user = self.session.query(self.Contact).filter_by(name=user_name).first()
        if user:
            print('Пользователь уже есть в контат листе')
        else:
            user = self.Contact(user_name)
            self.session.add(user)
            self.session.commit()
            print(f'Пользователь {user_name} добавлен в локальный контакт лист')

    def del_contact(self, user_name):
        user = self.session.query(self.Contact).filter_by(name=user_name).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            print(f'Пользователь {user_name} удалён из локального контакт листа')
        else:
            print('Пользователя с таким именем нет в локальном контакт листе')

    def add_message(self, user_name, text, status):
        """
        Ищем пользователя в контакт листе, если его нет то добавляем в контакт лист
        потом добавляем сообщение.
        :param user_name:
        :param text:
        :param status: str sent or received
        :return:
        """
        user = self.session.query(self.Contact).filter_by(name=user_name).first()
        if user:
            message = self.Message(user.id, text, status)
            self.session.add(message)
            self.session.commit()
        else:
            self.add_contact(user_name)
            self.add_message(user_name, text, status)

    def get_contacts(self):
        users = self.session.query(self.Contact).all()
        return users

    def get_history(self, user_name, day=1):
        """
        возвращает список obj сообщений с юзером. По умолчанию за последние сутки.
        :param day:
        :param user_name: str
        :return: list
        """
        user = self.session.query(self.Contact).filter_by(name=user_name).first()
        if not day == 'all':
            limit = datetime.now() - timedelta(days=day)
            messages = self.session.query(self.Message).filter(self.Message.contact_id == user.id,
                                                               self.Message.date_time > limit).order_by(
                self.Message.date_time).all()
        else:
            messages = self.session.query(self.Message).all()
        return messages

    def get_keys(self):
        '''
        Запрашивае ключи, если их нет то возвразаем False
        :return:
        '''
        keys = self.session.query(self.MyKey).first()
        if keys:
            return keys
        else:
            return False

    def add_keys(self,private_key,public_key):
        """
        Добавляем ключи
        :param private_key:
        :param public_key:
        :return:
        """
        keys = self.MyKey(private_key,public_key)
        self.session.add(keys)
        self.session.commit()


def main():
    client = ClientStorage('User-1')
    client.add_message('User-7', 'Привет go', 'sent')
    client.add_message('User-7', 'Привет сам', 'received')
    print(client.get_contacts())
    print(client.get_history('User-7'))


if __name__ == '__main__':
    main()
