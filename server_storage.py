from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import sqlite3
from datetime import datetime


class ServerStorage:
    class AllUser:
        def __init__(self, name, last_login_date):
            self.name = name
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

    def __init__(self):
        engine = create_engine('sqlite:///server_db.db3?check_same_thread=False', echo=False)
        Session = sessionmaker(bind=engine)
        """:type: sqlalchemy.orm.Session"""
        self.session = Session()
        self.meta_data = MetaData()
        clients_table = Table('all_users', self.meta_data,
                              Column('id', Integer, primary_key=True),
                              Column('name', String),
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

        self.meta_data.create_all(engine)
        mapper(self.AllUser, clients_table)
        mapper(self.ActiveUser, active_users)
        mapper(self.LoginHistory, login_history)
        self.clear_active_users()

    def create_user(self, name):
        """Добавляем нового пользователя, если он есть меняем дату последнего входа """
        user = self.session.query(self.AllUser).filter_by(name=name).first()
        if user:
            user.last_login_date = datetime.now()
        else:
            user = self.AllUser(name, datetime.now())
        self.session.add(user)
        self.session.commit()
        return user

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
        """ Создает нового пользователя, или меняет дату входа у старого,
        добавлет в активные и заносит в журнал истории логинов"""
        new_user = self.create_user(name)
        self.add_new_active_user(new_user.id, ip, port)
        history = self.LoginHistory(new_user.id, ip, port)
        self.session.add(history)
        self.session.commit()

    def delete_active_user(self, user_name):
        ''' Удаляет пользователя из активных '''
        user = self.session.query(self.AllUser).filter_by(name=user_name).first()
        user = self.session.query(self.ActiveUser).filter_by(user_id=user.id).first()
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


if __name__ == '__main__':
    server = ServerStorage()
    new_user = server.create_user('Vovas')
    server.add_new_active_user(new_user.id, '127.0.0.1', '7777')
    new_user_2 = server.create_user('Dima')
    server.add_new_active_user(new_user_2.id, '127.0.0.1', '7777')

    server.user_login('Vanya', '127.0.0.1', '8888')
    full_data = server.session.query(server.AllUser.name, server.ActiveUser.ip, server.AllUser.last_login_date).join(
        server.AllUser).all()
    print(full_data)
    server.user_login('Petya', '127.0.0.1', '8888')
    print('-------------')
    print(server.get_active_users(name='Vovas'))
    # server.delete_active_user('Vovas')
