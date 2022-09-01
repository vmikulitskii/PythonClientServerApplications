from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from datetime import datetime

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

    class Message(Base):
        __tablename__ = 'Messages'
        id = Column(Integer, primary_key=True)
        contact_id = Column(Integer, ForeignKey('Contacts.id'))
        text = Column(String)
        status = Column(String)
        date_time = Column(DateTime)

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
        engine = create_engine(f'sqlite:///client_db_{akk_name}.db3')
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


def main():
    client = ClientStorage('Vasya')
    client.add_message('Vasya-lo', 'Привет go', 'sent')
    client.add_message('Vasya-lo', 'Привет go', 'recieved')


if __name__ == '__main__':
    main()
