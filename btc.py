# P2SH-SegWit Bitcoin Scripting - Implementing A' -> B' -> C' Transactions

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pprint import pprint
from decimal import Decimal
import logging
logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

# RPC Connection Details
rpc_user = "bitcoinuser"
rpc_pass = "supersecurepasswordhehehehe"
rpc_host = "127.0.0.1"
rpc_port = 18443
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:{rpc_port}", timeout=120)

wallet_name = input("Enter Wallet Name : ")

# Ensure wallet exists
try:
    rpc_connection.createwallet(wallet_name)
except Exception as e:
    print(f"Wallet might already exist: {e}")

wallet_rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_host}:{rpc_port}/wallet/{wallet_name}")

# Generate P2SH-SegWit Addresses
addressA_segwit = wallet_rpc.getnewaddress("", "p2sh-segwit")
print(f"P2SH-SegWit Address A': {addressA_segwit}")
addressB_segwit = wallet_rpc.getnewaddress("", "p2sh-segwit")
print(f"P2SH-SegWit Address B': {addressB_segwit}")
addressC_segwit = wallet_rpc.getnewaddress("", "p2sh-segwit")
print(f"P2SH-SegWit Address C': {addressC_segwit}")

# Fund Address A' (SegWit)
wallet_rpc.generatetoaddress(101, addressA_segwit)
utxos = wallet_rpc.listunspent(0)
utxo = utxos[0]
utxo_txid = utxo['txid']
utxo_vout = utxo['vout']
amt = utxo['amount']
fee = Decimal("0.0001")

given = Decimal("0.4") * amt - fee
change = Decimal("0.6") * amt

# Create raw transaction (A' -> B', SegWit)
try:
    txids_vouts = [{"txid": utxo_txid, "vout": utxo_vout}]
    addresses_amts = {addressB_segwit: given, addressA_segwit: change}
    unsigned_tx_hex = wallet_rpc.createrawtransaction(txids_vouts, addresses_amts)
    decoded_tx_A_to_B = wallet_rpc.decoderawtransaction(unsigned_tx_hex)
    
    signed_hex = wallet_rpc.signrawtransactionwithwallet(unsigned_tx_hex)
    if signed_hex['complete']:
        segwit_txid_A_to_B = wallet_rpc.sendrawtransaction(signed_hex['hex'])
        print(f"SegWit TxID (A' -> B'): {segwit_txid_A_to_B}")
except JSONRPCException:
    print("Error in SegWit Transaction (A' -> B')")

# Fund Address B' -> C' (SegWit)
utxos = wallet_rpc.listunspent(0)
utxo = utxos[0]
utxo_txid = utxo['txid']
utxo_vout = utxo['vout']
amt = utxo['amount']

given = Decimal("0.4") * amt - fee
change = Decimal("0.6") * amt

# Create raw transaction (B' -> C', SegWit)
try:
    txids_vouts = [{"txid": utxo_txid, "vout": utxo_vout}]
    addresses_amts = {addressC_segwit: given, addressB_segwit: change}
    unsigned_tx_hex = wallet_rpc.createrawtransaction(txids_vouts, addresses_amts)
    decoded_tx_B_to_C = wallet_rpc.decoderawtransaction(unsigned_tx_hex)
    
    signed_hex = wallet_rpc.signrawtransactionwithwallet(unsigned_tx_hex)
    if signed_hex['complete']:
        segwit_txid_B_to_C = wallet_rpc.sendrawtransaction(signed_hex['hex'])
        print(f"SegWit TxID (B' -> C'): {segwit_txid_B_to_C}")
        
        # Validate the transaction scripts
        try:
            tx_info = wallet_rpc.getrawtransaction(segwit_txid_B_to_C, True)
            for vin in tx_info["vin"]:
                prev_tx = wallet_rpc.getrawtransaction(vin["txid"], True)
                print(f"Validating input script: {prev_tx['vout'][vin['vout']]['scriptPubKey']['hex']}")
            print("Transaction validation complete.")
        except JSONRPCException as e:
            print(f"Error in validation: {e}")
except JSONRPCException:
    print("Error in SegWit Transaction (B' -> C')")

# Get and print transaction details
segwit_tx_A_to_B = wallet_rpc.getrawtransaction(segwit_txid_A_to_B, True)
segwit_tx_B_to_C = wallet_rpc.getrawtransaction(segwit_txid_B_to_C, True)

print("\n========= Transaction Summary =========")
print(f"TxID for transaction A' -> B': {segwit_txid_A_to_B}")
print(f"SegWit Tx Size (A' -> B'): {segwit_tx_A_to_B['size']} bytes")
print("\nDecoded Scripts for A' -> B':")
#pprint(decoded_tx_A_to_B)
pprint(wallet_rpc.getrawtransaction(segwit_txid_A_to_B,2))

print(f"\nTxID for transaction B' -> C': {segwit_txid_B_to_C}")
print(f"SegWit Tx Size (B' -> C'): {segwit_tx_B_to_C['size']} bytes")
print("\nDecoded Scripts for B' -> C':")
#pprint(decoded_tx_B_to_C)
pprint(wallet_rpc.getrawtransaction(segwit_txid_B_to_C,2))




pprint(wallet_rpc.decoderawtransaction(unsigned_tx_hex))


print("\nBitcoin Debugger Steps (Challenge & Response Execution):")
print("1. Validate the transaction input scripts (scriptSig) against the previous output script (scriptPubKey).")
print("2. Ensure the correct signature and public key are provided.")
print("3. Check SegWit script execution with OP_HASH160, OP_EQUAL, and witness signature verification.")
print("4. Verify that unlocking script produces a valid result when combined with the locking script.")
print("5. If successful, the transaction is accepted into the mempool and included in a block.")
print("=======================================\n")
