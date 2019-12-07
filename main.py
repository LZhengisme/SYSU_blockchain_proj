#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QMainWindow
from gui.bank import Ui_Bank
from gui.companies import Ui_Companies
from gui.login import Ui_Login
from gui.manager import Ui_Manager
import os,sys,json,glob
from client.contractnote import ContractNote
from client.bcosclient import BcosClient
from eth_utils import to_checksum_address
from eth_utils.hexadecimal import encode_hex
from eth_account.account import Account
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
from client.bcoserror import BcosException, BcosError
from client_config import client_config
def list_api(file_pattern):
    """
    return list according to file_pattern
    """
    file_list = [f for f in glob.glob(file_pattern)]
    targets = []
    for file in file_list:
        targets.append(os.path.basename(file).split(".")[0])
    return targets

def list_accounts():
    """
    list all accounts
    """
    return list_api("bin/accounts/*.keystore")
    

class Bank(QMainWindow, Ui_Bank):
    def __init__(self, parent=None):
        super(Bank, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Platform for Bank")
        self.btn_authorize.clicked.connect(self.on_authorize)
        self.btn_quit.clicked.connect(self.on_quit)
        self.btn_reject.clicked.connect(self.on_reject)
    def on_authorize(self):
        QMessageBox.information(self,'Prompt','Authorize successfully!', QMessageBox.Ok)
        #TODO Table refresh

    def on_quit(self):
        self.close()

    def on_reject(self):
        QMessageBox.information(self,'Prompt','Reject successfully!', QMessageBox.Ok)
        #TODO Table refresh


class Companies(QMainWindow, Ui_Companies):
    def __init__(self, parent=None):
        super(Companies, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Platform for Companies")
        self.btn_quit.clicked.connect(self.on_quit)
        self.btn_reset_trans.clicked.connect(self.on_reset_transfer)
        self.btn_submit_trans.clicked.connect(self.on_submit_transfer)
        self.btn_reset_bor.clicked.connect(self.on_reset_borrowing)
        self.btn_submit_bor.clicked.connect(self.on_submit_borrowing)
        self.btn_reset_pur.clicked.connect(self.on_reset_purchase)
        self.btn_submit_pur.clicked.connect(self.on_submit_purchase)

        self.btn_transfer.clicked.connect(self.transfer_view)
        self.btn_purchasing.clicked.connect(self.purchase_view)
        self.btn_borrowing.clicked.connect(self.borrowing_view)
        self.btn_info.clicked.connect(self.info_view)

    def info_view(self):
        self.stackedWidget.setCurrentIndex(0)
    def transfer_view(self):
        self.stackedWidget.setCurrentIndex(1)
    def purchase_view(self):
        self.stackedWidget.setCurrentIndex(2)
    def borrowing_view(self):
        self.stackedWidget.setCurrentIndex(3)     
    def on_quit(self):
        self.close()
    def on_reset_transfer(self):
        self.line_trans_from.clear()
        self.line_trans_to.clear()
        self.line_trans_due.clear()
        self.line_trans_amt.clear()
    def on_submit_transfer(self):
        _from = self.line_trans_from.text()
        _to = self.line_trans_to.text()
        _due = self.line_trans_due.text()
        _amt = self.line_trans_amt.text()
        print(_from,_to,_due,_amt)
    def on_reset_borrowing(self):
        self.line_borr_amt.clear()
        self.line_borr_due.clear()
    def on_submit_borrowing(self):
        _amt = self.line_borr_amt.text()
        _due = self.line_borr_due.text()

    def on_reset_purchase(self):
        self.line_pur_amt.clear()
        self.line_pur_due.clear()
        self.line_pur_to.clear()
    def on_submit_purchase(self):
        _amt = self.line_pur_amt.text()
        _due = self.line_pur_due.text()
        _to = self.line_pur_to.text()      


class Manager(QMainWindow,Ui_Manager):
    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Platform for Blockchain managers")
        self.btn_register.clicked.connect(self.on_press_register)
        self.btn_select_register.clicked.connect(self.register_view)
        self.btn_select_list.clicked.connect(self.list_view)
        self.btn_quit.clicked.connect(self.close)
        self.btn_reset.clicked.connect(self.on_reset)

    def on_reset(self):
        self.edit_name.clear()
        self.edit_pwd.clear()
        self.edit_type.clear()

    def on_press_register(self):
        QMessageBox.information(self,'Prompt','Register successfully!', QMessageBox.Ok)

    def register_view(self):
        self.stackedWidget.setCurrentIndex(0)


    def list_view(self):
        self.stackedWidget.setCurrentIndex(1)
        self.list_info.clear()
        self.list_info.addItems(list_accounts())


    def get_name_pwd(self):
        return self.edit_name.text(),self.edit_pwd.text()

class Login(QMainWindow, Ui_Login):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Log In")
        self.btn_ok.clicked.connect(self.validate)
        self.btn_quit.clicked.connect(self.close)

    def validate(self):
        login_user = self.line_acc.text()
        login_password = self.line_pwd.text()
        # name = login_user
        # password = login_password
        # keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
        # # the account doesn't exists
        # if os.path.exists(keyfile) is False:
        #     raise BcosException("account {} doesn't exists".format(name))
        # print("show account : {}, keyfile:{} ,password {}  ".format(name, keyfile, password))
        # try:
        #     with open(keyfile, "r") as dump_f:
        #         keytext = json.load(dump_f)
        #         privkey = Account.decrypt(keytext, password)
        #         ac2 = Account.from_key(privkey)
        #         print("address:\t", ac2.address)
        #         print("privkey:\t", encode_hex(ac2.key))
        #         print("pubkey :\t", ac2.publickey)
        #         manager.show()
        #         self.close()
        # except Exception as e:
        #     QMessageBox.warning(self,
        #             "error",
        #             ("load account info for [{}] failed,"
        #                             " error info: {}!").format(name, e),
        #             QMessageBox.Yes)
        #     raise BcosException(("load account info for [{}] failed,"
        #                             " error info: {}!").format(name, e))
        if login_user == 'a' and login_password == 'a':
            manager_window.show()
            self.close()
        elif login_user == "bank" and login_password == "123456":
            bank_window.show()
            self.close()
        else:
            #TODO validate
            company_window.show()
            self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = Login()
    manager_window = Manager()
    bank_window = Bank()
    company_window = Companies()
    login_window.show()
    app.exec_()