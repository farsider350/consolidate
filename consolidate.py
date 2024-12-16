import json
import requests
import time

RPC_USER="rpcuser"
RPC_PASSWORD="rpcpassword"
RPC_PORT=3333
RPC_URL = 'http://127.0.0.1:'+str(RPC_PORT)
MIN_CONFS = 100
MAX_CONFS = 9999999
ADDRESS_TO_CONSOLIDATE_FROM = "address"
ADDRESS_TO_CONSOLIDATE_TO = "address"

def instruct_wallet(method, params):
    url = RPC_URL
    payload = json.dumps({"method": method, "params": params})
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request(
            "POST", url, data=payload, headers=headers, auth=(RPC_USER, RPC_PASSWORD))
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(e)
    except:
        print('No response from Wallet, check Bitcoin is running on this machine')

utxos = [];

def process_utxos_and_consolidate():
    unspent = instruct_wallet("listunspent", [1, 999999, [ADDRESS_TO_CONSOLIDATE_FROM]])
    
    for x in unspent["result"]: 
        utxos.append({"txid":x["txid"], "vout":x["vout"], "amount": x["amount"]})
    txes = []
    toSpend = 0
    for i, x in enumerate(utxos):
        print(i)
        txes.append({"txid":x["txid"], "vout":x["vout"]})
        toSpend += x["amount"]
        if(i > 0 and i % 25 == 0):
            amt = f"{toSpend-0.01:06f}"
            print(amt)
            cmd = instruct_wallet("createrawtransaction", [txes, {ADDRESS_TO_CONSOLIDATE_TO: amt}])
            if(cmd["result"] == None):
                print("Error: createrawtranaction failed.")
                print(cmd)
            cmd = instruct_wallet("signrawtransaction", [str(cmd["result"])])
            if(cmd["result"] == None):
                print("Error: signrawtransaction failed.")
                print(cmd)
            cmd = instruct_wallet("sendrawtransaction", [str(cmd['result']['hex'])])
            print(cmd)
            txes = []
            toSpend = 0
            time.sleep(3)
        time.sleep(0.1)

process_utxos_and_consolidate()
