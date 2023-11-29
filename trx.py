import requests
import json
import re
import execjs

def format_number(num):
    num_str = str(num)
    if len(num_str) > 6:
        formatted_num = num_str[:-6] + '.' + num_str[-6:]
    elif len(num_str) < 6 or len(num_str) == 6 :
        formatted_num = "0."+("0" * (6 - len(num_str)) + num_str)
    else:
        formatted_num = num_str
    return float(formatted_num)


# adding transaction to transactions.json file
def create_trans_in_json (hash):
    with open('transactions.json', 'r') as f:
        data = json.load(f)
    data.append(hash)
    with open('transactions.json', 'w') as f:
        json.dump(data, f)
        print("transaction created in .json")

# cheking if not transactions hash in json file ,if not adding transaction
def get_transaction_from_json(hash):
    with open('transactions.json') as json_file:
        hash_list = json.load(json_file)
    no_actived_tranz = []
    if not hash in hash_list:
        no_actived_tranz.append(hash)
        create_trans_in_json(hash)
    return no_actived_tranz

def get_transactions_from_net():
    wallet_address = "Your TRX wallet"
    url = f"https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=50&start=0&address={wallet_address}"
    response = requests.get(url)
    transactions = response.json()
    result_transactions = []
    for transaction in transactions['data']:
        if transaction["hash"] not in get_transaction_from_json(transaction["hash"]):
            money = format_number(transaction['contractData']['amount'])
            to_address = transaction['contractData']['to_address']
            owner_address = transaction['contractData']['owner_address']
            result_transactions.append([to_address,owner_address,money])
    return result_transactions




def is_tron_wallet(text):
    pattern = r"^(T|t)[a-zA-Z0-9]{33}$"
    match = re.match(pattern, text)
    return bool(match)


def send_tron(wallet,amount):
    js_code = """
    async function sendTransaction(toAddress, amount) {
        const TronWeb = require("tronweb")

        const tronWeb = new TronWeb({
            fullHost: 'https://api.trongrid.io',
            privateKey: 'Your TRX wallet privete key'
        });

        if (!tronWeb.isAddress(toAddress)) {
            throw new Error('Invalid recipient address');
        }

        if (isNaN(amount) || amount <= 0) {
            throw new Error('Invalid amount');
        }

        const account = await tronWeb.trx.getAccount();

        const transaction = await tronWeb.transactionBuilder.sendTrx(
            toAddress,
            amount,
            account.address
        );

        const signedTransaction = await tronWeb.trx.sign(transaction);

        const result = await tronWeb.trx.sendRawTransaction(signedTransaction);

        return result;
    }
    """
    ctx = execjs.compile(js_code)
    result = ctx.call("sendTransaction", wallet, amount)



