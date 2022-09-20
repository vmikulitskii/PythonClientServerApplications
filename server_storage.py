import configparser
import os.path

from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlite3
from datetime import datetime


class ServerStorage:
    class AllUser:
        def __init__(self, name, passwrd, last_login_date):
            self.name = name
            self.passwrd = passwrd
            self.last_login_date = last_login_date

            self.id = None

        def __repr__(self):
            return f'User - {self.name} - {self.last_login_date}'

    class ActiveUser:
        def __init__(self, user_id, ip, port):
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.id = None

        def __repr__(self):
            return f'User - {self.user_id} - {self.ip}- {self.port}'

    class LoginHistory:
        def __init__(self, user_id, ip, port):
            self.id = None
            self.user_id = user_id
            self.ip = ip
            self.port = port
            self.date_time = datetime.now()

        def __repr__(self):
            return f'User - {self.user_id} - {self.ip}- {self.port} - {self.date_time}'

    class Contact():

        def __init__(self, user_1, user_2):
            self.user_1_id = user_1
            self.user_2_id = user_2

        def __repr__(self):
            return f'{self.user_1_id} - {self.user_2_id}'

    class UserKey:
        def __init__(self, user_id, public_key):
            self.user_id = user_id
            self.public_key = public_key
            self.id = None

        def __repr__(self):
            return f'User - {self.user_id}'

    def __init__(self):
        # engine = create_engine('sqlite:///server_db.db3?check_same_thread=False', echo=False)
        config = configparser.ConfigParser()
        config.read('server_config.ini')
        db_path = config["SETTINGS"]["database_path"]
        db_name = config["SETTINGS"]["database_file"]
        db_abs_path = os.path.join(db_path, db_name)

        engine = create_engine(f'sqlite:///{db_abs_path}?check_same_thread=False', echo=False)
        Session = sessionmaker(bind=engine)
        # self.Base.metadata.create_all(engine)
        self.session = Session()
        self.meta_data = MetaData()
        clients_table = Table('all_users', self.meta_data,
                              Column('id', Integer, primary_key=True),
                              Column('name', String),
                              Column('passwrd', String),
                              Column('last_login_date', DateTime))

        active_users = Table('active_users', self.meta_data,
                             Column('id', Integer, primary_key=True),
                             Column('user_id', Integer, ForeignKey('all_users.id')),
                             Column('ip', String),
                             Column('port', String)
                             )
        login_history = Table('login_history', self.meta_data,
                              Column('id', Integer, primary_key=True),
                              Column('user_id', Integer, ForeignKey('all_users.id')),
                              Column('ip', String),
                              Column('port', String),
                              Column('date_time', DateTime)
                              )
        contacts = Table('contacts', self.meta_data,
                         Column('id', Integer, primary_key=True),
                         Column('user_1_id', Integer, ForeignKey('all_users.id')),
                         Column('user_2_id', Integer, ForeignKey('all_users.id'))
                         )

        keys = Table('keys', self.meta_data,
                         Column('id', Integer, primary_key=True),
                         Column('user_id', Integer, ForeignKey('all_users.id')),
                         Column('public_key', String)
                         )

        self.meta_data.create_all(engine)
        mapper(self.AllUser, clients_table)
        mapper(self.ActiveUser, active_users)
        mapper(self.LoginHistory, login_history)
        mapper(self.Contact, contacts)
        mapper(self.UserKey, keys)
        self.clear_active_users()

    def create_user(self, name,passwrd):
        """Добавляем нового пользователя, если он есть возвращаем False """
        user = self.session.query(self.AllUser).filter_by(name=name).first()
        if user:
            return False
        else:
            user = self.AllUser(name,passwrd, datetime.now())
            self.session.add(user)
            self.session.commit()
            return True

    def delete_user(self, name):
        """Удаляем пользователя"""
        user = self.session.query(self.AllUser).filter_by(name=name).first()
        if user:
            self.session.delete(user)
            self.session.commit()
        else:
            print('User не найден')

    def add_new_active_user(self, user_id, ip, port):
        """ Добавление пользователя в таблицу активных пользователей"""
        user = self.ActiveUser(user_id, ip, port)
        self.session.add(user)
        self.session.commit()
        return user

    def user_login(self, name, ip, port):
        """
        добавлет в активные и заносит в журнал истории логинов"""
        user = self.session.query(self.AllUser).filter_by(name=name).first()
        self.add_new_active_user(user.id, ip, port)
        history = self.LoginHistory(user.id, ip, port)
        self.session.add(history)
        self.session.commit()

    def get_user_pass(self,name):
        user = self.session.query(self.AllUser).filter_by(name=name).first()
        if user:
            return user.passwrd
        else:
            return False

    def delete_active_user(self, user_name):
        ''' Удаляет пользователя из активных '''
        if user_name:
            user = \
                self.session.query(self.AllUser, self.ActiveUser).filter_by(name=user_name).join(self.ActiveUser).first()[1]
            self.session.delete(user)
            self.session.commit()

    def clear_active_users(self):
        """ Очищает таблицу активных юзеров"""
        users = self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def get_login_history(self, name=None):
        history = self.session.query(self.AllUser.name, self.LoginHistory.ip, self.LoginHistory.port,
                                     self.LoginHistory.date_time).join(self.AllUser)
        if name:
            history = history.filter_by(name=name)

        return history.all()

    def get_active_users(self, name=None):
        users = self.session.query(self.AllUser.name, self.ActiveUser.ip, self.ActiveUser.port,
                                   self.AllUser.last_login_date).join(self.AllUser)
        if name:
            users = users.filter_by(name=name)

        return users.all()

    def add_new_contact(self, user_1, user_2):
        user_1 = self.session.query(self.AllUser).filter_by(name=user_1).first()
        user_2 = self.session.query(self.AllUser).filter_by(name=user_2).first()

        if user_1 and user_2:
            contact = self.session.query(self.Contact).filter_by(user_1_id=user_1.id, user_2_id=user_2.id)
            if contact.count() < 1:
                contact = self.Contact(user_1.id, user_2.id)
                self.session.add(contact)
                self.session.commit()
                return 201
            else:
                return 402
        else:
            return 401

    def delete_new_contact(self, user_1, user_2):
        user_1 = self.session.query(self.AllUser).filter_by(name=user_1).first()
        user_2 = self.session.query(self.AllUser).filter_by(name=user_2).first()

        if user_2:
            contact = self.session.query(self.Contact).filter_by(user_1_id=user_1.id, user_2_id=user_2.id).first()
            if contact:
                self.session.delete(contact)
                self.session.commit()
                return 203
            else:
                return 403
        else:
            return 401

    def get_contacts(self, user_name):
        """
        Получаем имя пользователя, возвращаем список имен его контактов
        :param user_name: str
        :return:
        """
        user = self.session.query(self.AllUser).filter_by(name=user_name).first()
        user_contacts = self.session.query(self.Contact, self.AllUser).filter_by(user_1_id=user.id).join(self.AllUser,
                                                                                                    self.AllUser.id == self.Contact.user_2_id).all()
        result = [contact[1].name for contact in user_contacts]
        return result

    def set_key(self,user_name,public_key):
        user = self.session.query(self.AllUser).filter_by(name=user_name).first()
        key = self.session.query(self.UserKey).filter_by(user_id = user.id).first()
        if key:
            if key.public_key != public_key:
                key.public_key = public_key
        else:
            key = self.UserKey(user.id,public_key)
        self.session.add(key)
        self.session.commit()

if __name__ == '__main__':
    server = ServerStorage()
    server.set_key('User-1','123')
    # new_user = server.create_user('Vovas','Paasword')
    # server.add_new_active_user(new_user.id, '127.0.0.1', '7777')
    # new_user_2 = server.create_user('Dima','Passwrd2')
    # server.add_new_active_user(new_user_2.id, '127.0.0.1', '7777')
    #
    # # server.user_login('Vanya', '127.0.0.1', '8888')
    # full_data = server.session.query(server.AllUser.name, server.ActiveUser.ip, server.AllUser.last_login_date).join(
    #     server.AllUser).all()
    # # print(full_data)
    # # server.user_login('Petya', '127.0.0.1', '8888')
    # print('-------------')
    # print(server.get_active_users(name='Vovas'))
    # server.delete_active_user('Vovas')
    #
    # query = server.session.query(server.AllUser, server.ActiveUser).outerjoin(server.ActiveUser)
    # query = server.session.query(server.AllUser, server.ActiveUser).outerjoin(server.ActiveUser)
    # print(query)
    # records = query
    # for user, active_user in records:
    #     # print(user.name,active_user.ip,active_user.port,user.last_login_date)
    #     print(user.name,
    #           f'Подключился {datetime.strftime(user.last_login_date, "%d.%m.%Y %H:%M")}' if active_user else 'Не активен')
    #     # print(user,active_user)

    # resp = server.add_new_contact('User-2', 'User-5')
    # print(resp)
    # resp = server.delete_new_contact('User-2', 'User-5')
    # print(resp)
    # contacts = server.get_contacts('User-17')
