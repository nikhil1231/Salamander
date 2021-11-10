from web3 import Web3
from . import consts
from logger.log import log
import time

class EVMTrader:

  def __init__(self, http_provider, native_token, native_token_addr, private_key, exchange_info, dev):
    self.web3 = Web3(Web3.HTTPProvider(http_provider))
    self.native_token = native_token
    self.addr = native_token_addr
    self.private_key = private_key
    self.exchange_addr = exchange_info['addr']
    self.exchange_contract = self.web3.eth.contract(address=exchange_info['addr'], abi=exchange_info['abi'])
    self.dev = dev

  def get_balance(self, token_addr):
    token_contract = self.web3.eth.contract(address=token_addr, abi=consts.ERC20_ABI)
    return token_contract.functions.balanceOf(consts.EVM_ADDRESS).call()

  def get_native_balance(self):
    return self.web3.fromWei(self.get_balance(self.addr), 'ether')

  def approve_token(self, token):
    print(f'Approving {token["name"]} for selling.')

    if self.dev: return

    token_addr = Web3.toChecksumAddress(token['tickers'][0]['base'])
    max_amount = self.web3.toWei(2**64-1,'ether')
    contract = self.web3.eth.contract(address=token_addr, abi=consts.ERC20_ABI)
    nonce = self.web3.eth.get_transaction_count(consts.EVM_ADDRESS)

    tx = contract.functions.approve(self.exchange_addr, max_amount).buildTransaction({
      'from': consts.EVM_ADDRESS,
      'nonce': nonce
    })

    signed_tx = self.web3.eth.account.signTransaction(tx, self.private_key)
    self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)


  def _get_txn_info(self, token):
    token_addr = Web3.toChecksumAddress(token['tickers'][0]['base'])
    nonce = self.web3.eth.get_transaction_count(consts.EVM_ADDRESS)

    return token_addr, nonce

  def buy_token(self, token, amount, dev=False):
    token_addr, nonce = self._get_txn_info(token)

    txn = self.contract_buy(
      0,
      [Web3.toChecksumAddress(self.addr), token_addr],
      consts.EVM_ADDRESS,
      int(time.time()) + 10000,
    ).buildTransaction({
      'from': consts.EVM_ADDRESS,
      'value': self.web3.toWei(amount, 'ether'),
      'gas': self.gas_limit,
      'gasPrice': self.web3.toWei(self.gas_price, 'gwei'),
      'nonce': nonce,
    })
    signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)

    log('buy', token['name'], token['asset_platform_id'], self.get_native_balance())

    if dev:
      print(f'DEV MODE: Bought {amount} {self.native_token} worth of {token["name"]}')
      return

    try:
      txn_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
      print(f'Bought {amount} {self.native_token} worth of {token["name"]}, txn hash ' + self.web3.toHex(txn_token))
      return self.web3.toHex(txn_token)
    except ValueError as err:
      print("Value error:" + str(err))

  def sell_token(self, token, ratio=1.0, dev=False):
    token_addr, nonce = self._get_txn_info(token)

    balance = self.get_balance(token_addr)

    txn = self.contract_sell(
      int(float(balance)*ratio),
      0,
      [token_addr, Web3.toChecksumAddress(self.addr)],
      consts.EVM_ADDRESS,
      int(time.time()) + 10000,
    ).buildTransaction({
      'from': consts.EVM_ADDRESS,
      'gas': self.gas_limit,
      'gasPrice': self.web3.toWei(self.gas_price, 'gwei'),
      'nonce': nonce,
    })
    signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)

    log('sell', token['name'], token['asset_platform_id'], self.get_native_balance())

    if dev:
      print(f'DEV MODE: Sold {ratio*100}% of {token["name"]}')
      return

    try:
      txn_token = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
      print(f'Sold {ratio*100}% of {token["name"]}, txn hash ' + self.web3.toHex(txn_token))
      return self.web3.toHex(txn_token)
    except ValueError as err:
      print("Value error:" + str(err))
