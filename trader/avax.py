from . import consts
from .evm import EVMTrader

class AvaxTrader(EVMTrader):
  def __init__(self, private_key, dev=False):
    super().__init__(
      "https://api.avax.network/ext/bc/C/rpc",
      'AVAX',
      consts.AVAX_ADDRESS,
      private_key,
      {
        'addr': consts.TRADER_JOE_ADDRESS,
        'abi': consts.TRADER_JOE_ABI,
      },
      dev
    )
    self.gas_limit = 5*10**5
    self.gas_price = 40

    self.contract_buy = self.exchange_contract.functions.swapExactAVAXForTokens
    self.contract_sell = self.exchange_contract.functions.swapExactTokensForAVAX
