from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox,QMainWindow
from manager import Manager
import sys
from client.contractnote import ContractNote
from client.bcosclient import BcosClient
import os,sys,json
from eth_utils import to_checksum_address
from eth_utils.hexadecimal import encode_hex
from eth_account.account import Account
from client.datatype_parser import DatatypeParser
from client.common.compiler import Compiler
from client.bcoserror import BcosException, BcosError
from client_config import client_config

name = ""
max_account_len = 240
if len(name) > max_account_len:
    sys.exit(1)
password = ""
print("starting : {} {} ".format(name, password))
ac = Account.create(password)
print("new address :\t", ac.address)
print("new privkey :\t", encode_hex(ac.key))
print("new pubkey :\t", ac.publickey)

kf = Account.encrypt(ac.privateKey, password)
keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
print("save to file : [{}]".format(keyfile))
with open(keyfile, "w") as dump_f:
    json.dump(kf, dump_f)
    dump_f.close()
print(">>-------------------------------------------------------")
print(
    "INFO >> read [{}] again after new account,address & keys in file:".format(keyfile))
with open(keyfile, "r") as dump_f:
    keytext = json.load(dump_f)
    privkey = Account.decrypt(keytext, password)
    ac2 = Account.from_key(privkey)
    print("address:\t", ac2.address)
    print("privkey:\t", encode_hex(ac2.key))
    print("pubkey :\t", ac2.publickey)
    print("\naccount store in file: [{}]".format(keyfile))
    print("\n**** please remember your password !!! *****")
    dump_f.close()
class Chain_manager(QMainWindow,Manager):
    def __init__(self, parent=None):
        super(Chain_manager, self).__init__(parent)
        self.setupUi(self)
        self.register_2.clicked.connect(self.end_event)
        self.btn_select_register.clicked.connect(self.on_pushButton1_clicked)
        self.btn_select_list.clicked.connect(self.on_pushButton2_clicked)
    # 登陆函数
    def end_event(self):
        QMessageBox.about(self, '登陆', '请输入姓名')
    def on_pushButton1_clicked(self):
        self.stackedWidget.setCurrentIndex(0)


    # 按钮二：打开第二个面板
    def on_pushButton2_clicked(self):
        self.stackedWidget.setCurrentIndex(1)



class login(QtWidgets.QMainWindow):
    def __init__(self):
        super(login, self).__init__()
        uic.loadUi('login.ui', self)
        self.show()
        self.pushButton_3.clicked.connect(self.validate)
    def validate(self):
        login_user = self.lineEdit.text()
        login_password = self.lineEdit_2.text()
        if login_user == 'a' and login_password == 'a':
            manager.show()
            self.close()
        else:
            QMessageBox.warning(self,
                    "error",
                    "Username or password is not valid!",
                    QMessageBox.Yes)
            self.lineEdit.setFocus()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = login()
    manager = Chain_manager()
    app.exec_()