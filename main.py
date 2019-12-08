#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox,QMainWindow, QTableWidgetItem
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
    

class Bank(QMainWindow, Ui_Bank):
    def __init__(self, parent=None):
        super(Bank, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Platform for Bank")
        self.btn_authorize.clicked.connect(self.on_authorize)
        self.btn_quit.clicked.connect(self.on_quit)
        self.btn_reject.clicked.connect(self.on_reject)
        self.table.setColumnCount(5)   ##设置列数
        self.headers = ['From','To','Amount','Status','Due date']
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.set_table_content()
        self.prompt.setText('Click one row to select.')

    def set_table_content(self):
        info_tuple = (('zl','srh','cc',),('srh','cc','rjj',),(30,50,1000,),('submitted','submitted','submitted',),('a','b','c',)) # TODO call contracts
        info_rows = len(info_tuple[0])
        for i in range(info_rows):
            row = self.table.rowCount()
            self.table.setRowCount(row + 1)
            self.table.setItem(row,0,QTableWidgetItem(info_tuple[0][i]))
            self.table.setItem(row,1,QTableWidgetItem(info_tuple[1][i]))
            self.table.setItem(row,2,QTableWidgetItem(str(info_tuple[2][i])))
            self.table.setItem(row,3,QTableWidgetItem(info_tuple[3][i]))
            self.table.setItem(row,4,QTableWidgetItem(info_tuple[4][i]))
    
    def on_authorize(self):
        if self.table.selectionModel().hasSelection():
            row = self.table.currentRow()
            args = [self.table.item(row, 0).text(), self.table.item(row, 1).text(), \
                int(self.table.item(row, 2).text()), "authorized",self.table.item(row, 4).text()]
            print(args)
            # TODO call contracts
            QMessageBox.information(self,'Prompt','Authorize successfully!', QMessageBox.Ok)
            self.table.setRowCount(0)
            self.set_table_content()
            #TODO Table refresh
        else:
            QMessageBox.warning(self,'Prompt','Please click to select a record!', QMessageBox.Ok)

    def on_quit(self):
        self.close()

    def on_reject(self):
        if self.table.selectionModel().hasSelection():
            row = self.table.currentRow()
            args = [self.table.item(row, 0).text(), self.table.item(row, 1).text(), \
                 int(self.table.item(row, 2).text()), "rejected",self.table.item(row, 4).text()]
            print(args)
            # TODO call contracts
            QMessageBox.information(self,'Prompt','Reject.', QMessageBox.Ok)
            self.table.setRowCount(0)
            self.set_table_content()
            #TODO Table refresh
        else:
            QMessageBox.warning(self,'Prompt','Please click to select a record!', QMessageBox.Ok)

class Companies(QMainWindow, Ui_Companies):
    def __init__(self, parent=None):
        super(Companies, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Platform for Companies")
        self.table_info_bor.setColumnCount(5)   ##设置列数
        self.headers = ['From','To','Amount','Status','Due date']
        self.table_info_bor.setHorizontalHeaderLabels(self.headers)

        self.table_info_lent.setColumnCount(5)   ##设置列数
        self.table_info_lent.setHorizontalHeaderLabels(self.headers)

        self.table_trans_lent.setColumnCount(5)   ##设置列数
        self.table_trans_lent.setHorizontalHeaderLabels(self.headers)

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

        self.table_info_bor.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table_info_lent.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table_trans_lent.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def set_basic_info(self, name):
        global client, contract_abi, to_address
        balance = client.call(to_address,contract_abi,"get_asset", [name])[0]
        self.set_table_info_borrowed_content(name)
        self.set_table_info_lent_content(name)
        self.set_table_trans_lent_content(name)
        total_borrowed = 0
        total_lent = 0
        for i in range(self.table_info_bor.rowCount()):
            total_borrowed += int(self.table_info_bor.item(i,2).text())
        for i in range(self.table_info_lent.rowCount()):
            total_lent += int(self.table_info_lent.item(i,2).text())
        self.line_basic_bal.setText(str(balance))
        self.line_basic_borr.setText(str(total_borrowed))
        self.line_basic_lent.setText(str(total_lent))
        self.dateTimeEdit.setDateTime(QDateTime.currentDateTime())


    def set_table_info_borrowed_content(self,name):
        global client, contract_abi, to_address
        info_tuple = client.call(to_address, contract_abi, "select", [name, 1])
        print("receipt:",info_tuple)

        # info_tuple = (('zl','srh','cc',),('srh','cc','rjj',),(30,50,1000,),('submitted','submitted','submitted',),('a','b','c',)) # TODO call contracts
        info_rows = len(info_tuple[0])
        for i in range(info_rows):
            row = self.table_info_bor.rowCount()
            self.table_info_bor.setRowCount(row + 1)
            self.table_info_bor.setItem(row,0,QTableWidgetItem(info_tuple[0][i]))
            self.table_info_bor.setItem(row,1,QTableWidgetItem(info_tuple[1][i]))
            self.table_info_bor.setItem(row,2,QTableWidgetItem(str(info_tuple[2][i])))
            self.table_info_bor.setItem(row,3,QTableWidgetItem(info_tuple[3][i]))
            self.table_info_bor.setItem(row,4,QTableWidgetItem(info_tuple[4][i]))
    
    def set_table_trans_lent_content(self,name):
        global client, contract_abi, to_address
        info_tuple = client.call(to_address, contract_abi, "select", [name, 0])
        print("receipt:",info_tuple)
        # info_tuple = (('zl','srh','cc',),('srh','cc','rjj',),(30,50,1000,),('submitted','submitted','submitted',),('a','b','c',)) # TODO call contracts
        info_rows = len(info_tuple[0])
        for i in range(info_rows):
            row = self.table_trans_lent.rowCount()
            self.table_trans_lent.setRowCount(row + 1)
            self.table_trans_lent.setItem(row,0,QTableWidgetItem(info_tuple[0][i]))
            self.table_trans_lent.setItem(row,1,QTableWidgetItem(info_tuple[1][i]))
            self.table_trans_lent.setItem(row,2,QTableWidgetItem(str(info_tuple[2][i])))
            self.table_trans_lent.setItem(row,3,QTableWidgetItem(info_tuple[3][i]))
            self.table_trans_lent.setItem(row,4,QTableWidgetItem(info_tuple[4][i]))
    
    def set_table_info_lent_content(self,name):
        global client, contract_abi, to_address
        info_tuple = client.call(to_address, contract_abi, "select", [name, 0])
        print("receipt:",info_tuple)
        # info_tuple = (('zl','srh','cc',),('srh','cc','rjj',),(30,50,1000,),('submitted','submitted','submitted',),('a','b','c',)) # TODO call contracts
        info_rows = len(info_tuple[0])
        for i in range(info_rows):
            row = self.table_info_lent.rowCount()
            self.table_info_lent.setRowCount(row + 1)
            self.table_info_lent.setItem(row,0,QTableWidgetItem(info_tuple[0][i]))
            self.table_info_lent.setItem(row,1,QTableWidgetItem(info_tuple[1][i]))
            self.table_info_lent.setItem(row,2,QTableWidgetItem(str(info_tuple[2][i])))
            self.table_info_lent.setItem(row,3,QTableWidgetItem(info_tuple[3][i]))
            self.table_info_lent.setItem(row,4,QTableWidgetItem(info_tuple[4][i]))
            
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
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.set_table_content()

    def set_table_content(self):
        global client, contract_abi, to_address
        receipt = client.call(to_address,contract_abi,"select_registered")
        print("receipt:",receipt)
        # info_tuple = (('zl','srh','cc',),('srh','cc','rjj',),('0xasdag','0x135214','0x1231',))
        info_tuple = receipt
        info_rows = len(info_tuple[0])
        for i in range(info_rows):
            row = self.table.rowCount()
            self.table.setRowCount(row + 1)
            self.table.setItem(row,0,QTableWidgetItem(info_tuple[0][i]))
            self.table.setItem(row,1,QTableWidgetItem(info_tuple[1][i]))
            self.table.setItem(row,2,QTableWidgetItem(info_tuple[2][i]))

    def on_reset(self):
        self.edit_name.clear()
        self.edit_pwd.clear()
        self.edit_type.clear()

    def on_press_register(self):
        name, password, _type = self.edit_name.text(), self.edit_pwd.text(), self.edit_type.text()
        max_account_len = 240
        if len(name) > max_account_len:
            QMessageBox.warning(self, 'Error', 'The name should not exceed 240 characters!')
            sys.exit(1)
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

        global client, contract_abi, to_address
        args = [name, ac.address, 'Company']
        # res = client.call(str('0x0559deb98ded0b3f2953490e77e4adf4773ac16d'),contract_abi,"register",args)
        # print("result :",res)
        print(name)        
        receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"register",args)
        print("receipt:",receipt['output'])


        QMessageBox.information(self,'Prompt','Register successfully!', QMessageBox.Ok)

    def register_view(self):
        self.stackedWidget.setCurrentIndex(0)


    def list_view(self):
        self.stackedWidget.setCurrentIndex(1)
        self.table.setRowCount(0)
        self.set_table_content()


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
        name = self.line_acc.text()
        password = self.line_pwd.text()
        if name == 'admin' and password == 'admin':
            manager_window.show()
            self.close()
        elif name == "bank" and password == "123456":
            bank_window.show()
            self.close()
        else:
            keyfile = "{}/{}.keystore".format(client_config.account_keyfile_path, name)
            # the account doesn't exists
            if os.path.exists(keyfile) is False:
                QMessageBox.warning(self,
                        "error",
                        "account {} doesn't exists".format(name),
                        QMessageBox.Yes)
                raise BcosException("account {} doesn't exists".format(name))
            print("show account : {}, keyfile:{} ,password {}  ".format(name, keyfile, password))
            try:
                with open(keyfile, "r") as dump_f:
                    keytext = json.load(dump_f)
                    privkey = Account.decrypt(keytext, password)
                    ac2 = Account.from_key(privkey)
                    print("address:\t", ac2.address)
                    print("privkey:\t", encode_hex(ac2.key))
                    print("pubkey :\t", ac2.publickey)
                    company_window.show()
                    company_window.set_basic_info(name)
                    self.close()
            except Exception as e:
                QMessageBox.warning(self,
                        "error",
                        ("load account info for [{}] failed,"
                                        " error info: {}!").format(name, e),
                        QMessageBox.Yes)


if __name__ == "__main__":
    # if os.path.isfile(client_config.solc_path) or os.path.isfile(client_config.solcjs_path):
        # Compiler.compile_file("contracts/TableTest.sol")
    abi_file = "contracts/TableTest.abi"
    data_parser = DatatypeParser()
    data_parser.load_abi_file(abi_file)
    contract_abi = data_parser.contract_abi
    client = BcosClient()
    # print(client.getinfo())
    # print("\n>>Deploy:----------------------------------------------------------")
    # with open("contracts/TableTest.bin", 'r') as load_f:
    #     contract_bin = load_f.read()
    #     load_f.close()
    # result = client.deploy(contract_bin)
    # print("deploy", result)
    # print("new address : ", result["contractAddress"])
    # contract_name = os.path.splitext(os.path.basename(abi_file))[0]
    # memo = "tx:" + result["transactionHash"]
    # # 把部署结果存入文件备查
    # ContractNote.save_address(contract_name,
    #                         result["contractAddress"],
    #                         int(result["blockNumber"], 16), memo)
    # to_address = result['contractAddress']  # use new deploy address
    to_address = '0xe05b4dbef2b70c251f26752adc995c018764315e'
    # receipt = client.call(to_address,contract_abi,"create")
    # print("receipt:",receipt)
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"create_company_table")
    # print("receipt:",receipt)
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"create_receipt_table")
    # print("receipt:",receipt)
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"insert",["shirunhao", "baoye", 250, "submitted", "tom"])
    # print("receipt:",receipt)
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"register",["shirunhao", "srh", "tom"])
    # print("receipt:",receipt['output'])
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"register",["baoye", "by", "tom"])
    # print("receipt:",receipt['output'])
    # receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"purchasing",["srh", "by", 250, "tom"])
    # print("receipt:",receipt['output'])
    # receipt = client.call(to_address,contract_abi,"select",["shirunhao",0])
    # print("receipt:",receipt)
    # receipt = client.sendRawTransactionGetReceipt('0x4e5ddc8943d07c61c034303407e58f7b3289ff21',contract_abi,"create_receipt_table")
    # # print("\n>>parse receipt and transaction:----------------------------------------------------------")
    # logresult = data_parser.parse_event_logs(receipt["logs"])
    # i = 0
    # for log in logresult:
    #     if 'eventname' in log:
    #         i = i + 1
    #         print("{}): log name: {} , data: {}".format(i,log['eventname'],log['eventdata']))
    # receipt = client.sendRawTransactionGetReceipt('0x4e5ddc8943d07c61c034303407e58f7b3289ff21',contract_abi,"create_companies_table")

    # print("\n>>parse receipt and transaction:----------------------------------------------------------")
    # logresult = data_parser.parse_event_logs(receipt["logs"])
    # i = 0
    # for log in logresult:
    #     if 'eventname' in log:
    #         i = i + 1
    #         print("{}): log name: {} , data: {}".format(i,log['eventname'],log['eventdata']))
    # args = [to_checksum_address('0x22b99c4c079f879032e8b3b61d48dd6b0c9c6463'), 
    # to_checksum_address('0x1fdc502734ad516d0b85b2ce55d1fa17c46ce49a'), 250, 'tom']
    # receipt = client.sendRawTransactionGetReceipt(str('0x4e5ddc8943d07c61c034303407e58f7b3289ff21'),contract_abi,"select_one",[0])#to_checksum_address('0x22b99c4c079f879032e8b3b61d48dd6b0c9c6463')])
    # # receipt = client.sendRawTransactionGetReceipt(str('0x39d0a8836cabd9f1f1d76e9921decd2f4dbd3c5c'),contract_abi,"get_cnt")
    # print("\n>>parse receipt and transaction:----------------------------------------------------------")
    # logresult = data_parser.parse_event_logs(receipt["logs"])
    # i = 0
    # for log in logresult:
    #     if 'eventname' in log:
    #         i = i + 1
    #         print("{}): log name: {} , data: {}".format(i,log['eventname'],log['eventdata']))
    # print("receipt:",receipt)
    app = QtWidgets.QApplication(sys.argv)
    login_window = Login()
    manager_window = Manager()
    bank_window = Bank()
    company_window = Companies()
    login_window.show()
    app.exec_()
    client.finish()
