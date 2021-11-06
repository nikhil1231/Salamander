from web3 import Web3
from . import consts
import time

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

def approve_token(token_addr, private_key):
  print(f'Approving {token_addr} for selling.')

  token_addr = Web3.toChecksumAddress(token_addr)
  max_amount = web3.toWei(2**64-1,'ether')
  contract = web3.eth.contract(address=token_addr, abi=consts.ERC20_ABI)
  nonce = web3.eth.get_transaction_count(consts.BSC_ADDRESS)

  tx = contract.functions.approve(consts.PANCAKE_ADDRESS, max_amount).buildTransaction({
    'from': consts.BSC_ADDRESS,
    'nonce': nonce
  })

  signed_tx = web3.eth.account.signTransaction(tx, private_key)
  web3.eth.sendRawTransaction(signed_tx.rawTransaction)

def buy_token(token_addr, bnb_amount, private_key, gas_price=5, dev=False):
  print("buying " + token_addr)

  token_addr = Web3.toChecksumAddress(token_addr)
  contract = web3.eth.contract(address=consts.PANCAKE_ADDRESS, abi=consts.PANCAKE_ABI)
  nonce = web3.eth.get_transaction_count(consts.BSC_ADDRESS)

  txn = contract.functions.swapExactETHForTokens(
    0,
    [Web3.toChecksumAddress(consts.WBNB_ADDRESS), token_addr],
    consts.BSC_ADDRESS,
    int(time.time()) + 10000,
  ).buildTransaction({
    'from': consts.BSC_ADDRESS,
    'value': web3.toWei(bnb_amount, 'ether'),
    'gas': 5*10**5,
    'gasPrice': web3.toWei(gas_price, 'gwei'),
    'nonce': nonce,
  })
  signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

  if dev:
    print(f'DEV MODE: Bought {bnb_amount} BNB worth of {token_addr}')
    return

  try:
    txn_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Bought {bnb_amount} BNB worth of {token_addr}, txn hash " + web3.toHex(txn_token))
    return web3.toHex(txn_token)
  except ValueError as err:
    print("Value error:" + str(err))

def sell_token(token_addr, private_key, ratio=1.0, dev=False):
  print(f"Selling {ratio*100}% of {token_addr}")

  token_addr = Web3.toChecksumAddress(token_addr)

  contract = web3.eth.contract(address=consts.PANCAKE_ADDRESS, abi=consts.PANCAKE_ABI)

  nonce = web3.eth.get_transaction_count(consts.BSC_ADDRESS)

  token_contract = web3.eth.contract(address=token_addr, abi=consts.ERC20_ABI)
  balance = token_contract.functions.balanceOf(consts.BSC_ADDRESS).call()

  txn = contract.functions.swapExactTokensForETH(
    int(balance*ratio),
    0,
    [token_addr, Web3.toChecksumAddress(consts.WBNB_ADDRESS)],
    consts.BSC_ADDRESS,
    int(time.time()) + 10000,
  ).buildTransaction({
    'from': consts.BSC_ADDRESS,
    'gas': 5*10**5,
    'gasPrice': web3.toWei('5', 'gwei'),
    'nonce': nonce,
  })
  signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)

  if dev:
    print(f'DEV MODE: Sold {ratio*100}% of {token_addr}')
    return

  try:
    txn_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Sold {ratio*100}% of {token_addr}, txn hash " + web3.toHex(txn_token))
    return web3.toHex(txn_token)
  except ValueError as err:
    print("Value error:" + str(err))
