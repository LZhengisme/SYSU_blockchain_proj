#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

if os.path.isfile(client_config.solc_path) or os.path.isfile(client_config.solcjs_path):
    Compiler.compile_file("contracts/SupplyCF.sol")
abi_file = "contracts/SupplyCF.abi"
data_parser = DatatypeParser()
data_parser.load_abi_file(abi_file)
contract_abi = data_parser.contract_abi
client = BcosClient()
print(client.getinfo())
print("\n>>Deploy:----------------------------------------------------------")
with open("contracts/SupplyCF.bin", 'r') as load_f:
    contract_bin = load_f.read()
    load_f.close()
result = client.deploy(contract_bin)
print("deploy", result)
print("new address : ", result["contractAddress"])
contract_name = os.path.splitext(os.path.basename(abi_file))[0]
memo = "tx:" + result["transactionHash"]
# 把部署结果存入文件备查
ContractNote.save_address(contract_name,
                        result["contractAddress"],
                        int(result["blockNumber"], 16), memo)
to_address = result['contractAddress']  # use new deploy address
receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"create_company_table")
print("receipt:",receipt['output'])
receipt = client.sendRawTransactionGetReceipt(to_address,contract_abi,"create_receipt_table")
print("receipt:",receipt['output'])