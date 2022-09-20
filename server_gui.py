import pathlib
import sys
from collections import namedtuple

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog
from server_gui_main_ui import Ui_MainWindow
from sevrer_gui_history_ui import Ui_Dialog as History_Ui_Dialog
from server_gui_settings_ui import Ui_Dialog as ServerSettings_Ui_Dialog
from server_gui_registration_ui import Ui_regNewUserDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from server_storage import ServerStorage
from datetime import datetime
from PyQt5.QtCore import Qt
from os import path
import pathlib
import configparser


class MyWindow(QMainWindow, Ui_MainWindow):
    def get_active_users_model(self, database):
        users = database.get_active_users()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Имя', 'ip', 'port', 'Дата и время подключения'])
        for user in users:
            name, ip, port, date = user
            item_0 = QStandardItem(name)
            item_0.setEditable(False)
            item_0.setTextAlignment(Qt.AlignCenter)

            item_1 = QStandardItem(ip)
            item_1.setEditable(False)
            item_1.setTextAlignment(Qt.AlignCenter)

            item_2 = QStandardItem(port)
            item_2.setEditable(False)
            item_2.setTextAlignment(Qt.AlignCenter)

            item_3 = QStandardItem(datetime.strftime(date, "%d.%m.%Y %H:%M"))
            item_3.setEditable(False)
            item_3.setTextAlignment(Qt.AlignCenter)

            model.appendRow([item_0, item_1, item_2, item_3])
            self.active_users_table.resizeColumnsToContents()
        return model

    def __init__(self):
        QMainWindow.__init__(self, parent=None)
        self.setupUi(self)



class UserHistory(QDialog, History_Ui_Dialog):
    def get_users_history_model(self, database):
        """
        Получаем обтект с базой, возвращаем Модель QStandardItemModel для таблицы
        позже надо добавить количество отправленых сообщений(пока их в базе нет)
        :param database:
        :return:
        """
        users = database.get_login_history()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Имя', 'ip', 'port', 'Дата и время подключения'])
        for user in users:
            name, ip, port, date = user
            item_0 = QStandardItem(name)
            item_0.setEditable(False)
            item_0.setTextAlignment(Qt.AlignCenter)

            item_1 = QStandardItem(ip)
            item_1.setEditable(False)
            item_1.setTextAlignment(Qt.AlignCenter)

            item_2 = QStandardItem(port)
            item_2.setEditable(False)
            item_2.setTextAlignment(Qt.AlignCenter)

            item_3 = QStandardItem(datetime.strftime(date, "%d.%m.%Y %H:%M"))
            item_3.setEditable(False)
            item_3.setTextAlignment(Qt.AlignCenter)

            model.appendRow([item_0, item_1, item_2, item_3])
        return model

    def __init__(self):
        QDialog.__init__(self, parent=None)
        self.setupUi(self)
        self.exitButton.clicked.connect(self.close)


class ServerSettings(QDialog, ServerSettings_Ui_Dialog):
    @staticmethod
    def get_settings():
        """
        Считывыем ini файл и возвращаем namedtuple c настройками
        :return:
        """
        config = configparser.ConfigParser()
        abs_path = path.abspath(__file__)
        dir, filname = path.split(abs_path)
        config_path = path.join(dir, 'server_config.ini')
        config.read(config_path)

        result = namedtuple('Settings', 'database_path default_port database_file listen_address')

        result.database_path = config['SETTINGS']['database_path']
        result.default_port = config['SETTINGS']['default_port']
        result.database_file = config['SETTINGS']['database_file']
        result.listen_address = config['SETTINGS']['listen_address']
        return result

    def set_settings(self):
        """
        Сохраняем настройки в файл и выводим окно оповещения
        :return:
        """
        config = configparser.ConfigParser()
        abs_path = path.abspath(__file__)
        dir, filname = path.split(abs_path)
        config_path = path.join(dir, 'server_config.ini')
        config['SETTINGS'] = {}
        config['SETTINGS']['database_path'] = self.dbPathEdit.text()
        config['SETTINGS']['default_port'] = self.dbPortNameEdit.text()
        config['SETTINGS']['database_file'] = self.dbNameEdit.text()
        config['SETTINGS']['listen_address'] = self.dbIpNameEdit.text()

        try:
            port = int(self.dbPortNameEdit.text())
            if port > 65535 or port < 1024:
                raise ValueError
            else:
                with open(config_path, 'w', encoding='utf-8') as file:
                    config.write(file)
                msg_text = 'Настройки сохранены'
        except ValueError:
            msg_text = 'Порт должен быть числом от 1024 до 65535'

        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Сохранение настроек')
        msg.setText(msg_text)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)

        msg.exec_()

    def browse_folser(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,'Выберите директорию в которой лежит файл с базой')
        if directory:
            self.dbPathEdit.setText(directory)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ExitButton.clicked.connect(self.close)
        settings = self.get_settings()
        self.dbPathEdit.setText(settings.database_path)
        self.dbNameEdit.setText(settings.database_file)
        if settings.listen_address:
            self.dbIpNameEdit.setText(settings.listen_address)
        self.dbPortNameEdit.setText(settings.default_port)

        self.SaveButton.clicked.connect(self.set_settings)
        self.pushDbPathButton.clicked.connect(self.browse_folser)

class Registration(QDialog, Ui_regNewUserDialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.passEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    server_db = ServerStorage()
    server_db.user_login('Vanya', '127.0.0.1', '8888')
    server_db.user_login('Petya', '127.0.0.1', '8888')
    server_db.user_login('Kirill', '127.0.0.1', '8888')

    history_window = UserHistory()
    server_settings = ServerSettings()
    window.show()
    window.users_history.triggered.connect(history_window.show)
    window.server_settings.triggered.connect(server_settings.show)
    history_window.users_history_table.setModel(history_window.get_users_history_model(server_db))
    history_window.users_history_table.resizeColumnsToContents()
    window.active_users_table.setModel(window.get_active_users_model(server_db))
    window.active_users_table.resizeColumnsToContents()
    sys.exit(app.exec_())
