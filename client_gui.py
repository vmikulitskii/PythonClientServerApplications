""" Gui для клиентской части мессенджера"""

import datetime
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QMainWindow

from client_gui_arrived_message_ui import Ui_newMesaageDialog
from client_gui_log_pass_ui import Ui_loginPasswrdDialog
from client_gui_main_ui import Ui_MainWindow
from client_gui_new_localcontact_ui import Ui_addNewLocalContactDialog
from client_storage import ClientStorage
from common.variables import RECEIVED, SENT


class MyWindow(QMainWindow, Ui_MainWindow):
    ''' Основное окно клиентской части приложения'''
    contact_selected = pyqtSignal(QtWidgets.QListWidgetItem)

    def view_contacts(self):
        """
        Загружаем и показываем список контактов
        :return:
        """
        contacts = self.client_db.get_contacts()
        # model = QStandardItemModel()
        # self.listContacts.setModel(model)
        for contact in contacts:
            self.listContacts.addItem(contact.name)
            # item = QStandardItem(contact.name)
            # item.setBackground(QColor('#ffff99'))
            # model.appendRow(item)

    def __init__(self, database):
        super().__init__()
        self.setupUi(self)
        self.actionExit.triggered.connect(QtWidgets.qApp.exit)
        self.client_db = database
        self.activ_contact_name = None

        self.listContacts.itemDoubleClicked.connect(self.on_change_contact)

    def on_change_contact(self, value):
        self.contact_selected.emit(value)

    def load_last_history(self, user_name):
        """
        Загружаем переписку за последние сутки с определенным контактом
        и показываем в нашей Qtableview
        :param user_name: str
        :return:
        """
        last_messages = self.client_db.get_history(user_name)
        model = QStandardItemModel()
        self.tableMessage.setModel(model)
        last_msg_status = ''
        for msg in last_messages:
            time = datetime.datetime.strftime(msg.date_time, '%H:%M')
            user_name = 'Я:' if msg.status == SENT else f'{msg.Contact.name}:'
            if last_msg_status == msg.status:
                parts = [time, msg.text]
            else:
                parts = [user_name, time, msg.text]
            for part in parts:
                item = QStandardItem(part)
                item.setEditable(False)
                if msg.status == SENT:
                    item.setTextAlignment(Qt.AlignRight)
                    item.setBackground(QColor('#c1e8ce'))
                elif msg.status == RECEIVED:
                    item.setTextAlignment(Qt.AlignLeft)
                    item.setBackground(QColor('#fceaca'))
                model.appendRow([item])
            last_msg_status = msg.status

        self.tableMessage.horizontalHeader().setDefaultSectionSize(490)
        self.tableMessage.resizeRowsToContents()

        self.tableMessage.setShowGrid(False)
        self.tableMessage.horizontalHeader().setVisible(False)
        self.tableMessage.verticalHeader().setVisible(False)
        self.tableMessage.scrollToBottom()

    @pyqtSlot(QtWidgets.QListWidgetItem)
    def get_user_message(self, contact_obj):
        """ Слот, при получении сигнала загружает сообщения и меняет активного контакта"""
        self.load_last_history((contact_obj.text()))
        self.activ_contact_name = contact_obj.text()
        print(f'Активирован контакт - {self.activ_contact_name}')

    def make_connection(self, contact_list):
        contact_list.itemDoubleClicked.connect(self.get_user_message)


class ArrivedMessage(QDialog, Ui_newMesaageDialog):
    '''Окно сообщающее что получено новое сообнение'''

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class NewLocalContact(QDialog, Ui_addNewLocalContactDialog):
    """Окно локального добавления нового контакта """

    def __init__(self):
        super().__init__()
        self.setupUi(self)


class LoginPass(QDialog, Ui_loginPasswrdDialog):
    """ Окно для ввода логина и пароля"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.passEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def edit_clear(self):
        self.loginEdit.clear()
        self.passEdit.clear()


def main():

    client_db = ClientStorage('User-1')
    # client_db.add_contact('User-1')
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow(client_db)
    # window.make_connection(window.listContacts)
    window.show()
    # # window.load_last_history('User-8')
    # # am = ArrivedMessage('Vasia')
    # # am.show()

    window.view_contacts()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
