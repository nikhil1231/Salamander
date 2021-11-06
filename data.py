import requests
from scraper.new_coins import get_recent_coins
from matplotlib import pyplot as plt
import numpy as np

plt.style.use('dark_background')


def get_prices(coin_id):
  r = requests.get('https://api.coingecko.com/api/v3/coins/' + coin_id + '/market_chart?vs_currency=usd&days=1')
  return r.json()['prices']

def get_returns(prices):
  initial = prices[0]
  return [price / initial for price in prices]

def analyse_coins(coins):
  data = [get_returns(list(zip(*get_prices(coin)))[1]) for coin in coins]

  for coin in data:
    plt.plot(np.arange(0, len(coin)), coin)

  avg = [np.prod(points) for points in zip(*data)]

  plt.plot(np.arange(0, len(avg)), avg, linestyle='dashed', linewidth=2)


if __name__ == '__main__':
  coins = requests.get('https://api.coingecko.com/api/v3/coins/list').json()
  new_coins = get_recent_coins(chains=['BSC'], max_coins=50)[1:]

  filtered_coins = [coin['id'] for coin in coins for new_coin in new_coins if coin['name'] == new_coin.name]

  analyse_coins(filtered_coins)

  plt.show()