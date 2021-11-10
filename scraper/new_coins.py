import requests
from .parser import get_parsed_recent_coins
from .coins_persistence import read_latest_coin, store_latest_coin

CHAIN_MAP = {
  'BSC': 'Binance Smart Chain',
  'ETH': 'ethereum',
  'SOL': 'Solana',
  'AVAX': 'Avalanche',
  'MATIC': 'Polygon POS',
}

def filter_coins(coins, chains=[], max_coins=3):
  res = list(filter(lambda x: x.chain in map(lambda y: CHAIN_MAP[y], chains), coins))
  return res[:max_coins] if len(res) > max_coins else res

def get_recent_coins(chains=[], max_coins=3):
  return filter_coins(get_parsed_recent_coins(), chains, max_coins)

def get_coin_address(coin_id):
  # TODO: ensure r.json()['tickers']['target'] == 'WBNB'
  return requests.get('https://api.coingecko.com/api/v3/coins/' + coin_id).json()

def toApi(new_coins):
  coins = requests.get('https://api.coingecko.com/api/v3/coins/list').json()
  coin_ids = [coin['id'] for coin in coins for new_coin in new_coins if coin['name'] == new_coin.name]
  return [get_coin_address(id) for id in coin_ids]

def get_new_coins(chains=[], max_coins=3, force_fresh=False):
  old_coin_ticker = "" if force_fresh else read_latest_coin()

  new_coins = get_parsed_recent_coins()
  new_coin_tickers = [coin.ticker for coin in new_coins]

  res = new_coins

  for i, ticker in enumerate(new_coin_tickers):
    if ticker == old_coin_ticker:
      res = new_coins[:i]
      break

  res = filter_coins(res, chains, max_coins)

  if len(res) == 0:
    return []

  api_coins = toApi(res)

  store_latest_coin(api_coins[0])

  return api_coins

if __name__ == "__main__":
  print(get_new_coins())
