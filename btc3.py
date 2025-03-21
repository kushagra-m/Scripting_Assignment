from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
from decimal import Decimal
import logging
logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)
# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_user = "bitcoinuser"
rpc_pass = "supersecurepasswordhehehehe"
rpc_host = "127.0.0.1"
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:18443", timeout=120)
rpc_port= 18443 
# Create and load the wallet (if not already loaded)
wallet_name = input("Enter Wallet Name : ")

# Ensure wallet exists
try:
    rpc_connection.loadwallet(wallet_name)
except Exception as e:
    print(f"Error in loading")

# Now, reconnect specifying the wallet
wallet_rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

#Load the available addresses and figure out which one is B
#B is typically the one with lesser balance 
addressC = wallet_rpc.getnewaddress("", "legacy")
print(f"Legacy Address C: {addressC}")

utxo_txid =0
utxo_vout = 0
amt = Decimal(str(0.0))
#find txID for the last A to B transaction
all_utxos = wallet_rpc.listunspent(0)
u0= all_utxos[0]
u1= all_utxos[1]
if u0["amount"]>u1["amount"]:
    addressB = u1["address"]
    utxo_txid= u1["txid"]
    utxo_vout= u1["vout"]
    amt = u1["amount"]
else:
    addressB = u0["address"]
    utxo_txid= u0["txid"]
    utxo_vout= u0["vout"]
    amt = u0["amount"]

print(f"address of B: {addressB}")

fee=0.0001
dec_fee = Decimal(str(fee))
given= Decimal(str(0.4))*amt-dec_fee
change= Decimal(str(0.6))*amt
#create raw transaction
try:
    txids_vouts = [{"txid": utxo_txid, "vout": utxo_vout}]
    addresses_amts = {f"{addressC}": given, f"{addressB}": change} #fee automatically accounted for
    unsigned_tx_hex = wallet_rpc.createrawtransaction(txids_vouts, addresses_amts)
    print(f"the unsigned tx \n {unsigned_tx_hex} \n")
    #decoding the raw transaction
    pprint(wallet_rpc.decoderawtransaction(unsigned_tx_hex))
    print("\n \n ")

    #signing the transaction USING WALLET
    signed_hex = wallet_rpc.signrawtransactionwithwallet(unsigned_tx_hex)
    if signed_hex['complete']:
        print(f"the signed hex \n {signed_hex} \n ")
        send_tx = wallet_rpc.sendrawtransaction(signed_hex['hex'])
        print(f"The final TxID is \n {send_tx} \n")
        print("\n \n")
        pprint(wallet_rpc.getrawtransaction(send_tx,2))
        pprint(wallet_rpc.gettransaction(send_tx))
        pprint(wallet_rpc.decoderawtransaction(unsigned_tx_hex))
    else:
        print("Error")

    
except JSONRPCException:
    print("Error")
