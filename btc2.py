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
    rpc_connection.createwallet(wallet_name)
except Exception as e:
    print(f"Wallet might already exist: {e}")

# Now, reconnect specifying the wallet
wallet_rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Generate a new legacy (P2PKH) address
addressA = wallet_rpc.getnewaddress("", "legacy")
print(f"Legacy Address A: {addressA}")
addressB = wallet_rpc.getnewaddress("", "legacy")
print(f"Legacy Address B: {addressB}")

# Generate 101 blocks to this address
wallet_rpc.generatetoaddress(101, addressA)
utxos = wallet_rpc.listunspent(0)
utxo= utxos[0]
utxo_txid = utxo['txid']
utxo_vout = utxo['vout']
amt = utxo['amount']
fee=0.0001
dec_fee = Decimal(str(fee))
given= Decimal(str(0.4))*amt-dec_fee
change= Decimal(str(0.6))*amt
#create raw transaction
try:
    txids_vouts = [{"txid": utxo_txid, "vout": utxo_vout}]
    addresses_amts = {f"{addressB}": given, f"{addressA}": change} #fee automatically accounted for
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

# Check wallet balance
"""wallet_info = wallet_rpc.getwalletinfo()
pprint(wallet_info)"""


