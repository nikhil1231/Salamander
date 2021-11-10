import csv
import os

COINS_PATH = 'data/coins.csv'

def read_latest_coin():
  if not os.path.exists(COINS_PATH):
    return ""

  with open(COINS_PATH, newline='') as f:
    reader = csv.reader(f)
    return next(reader)[0]

def store_latest_coin(coin):
  with open(COINS_PATH, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([coin['symbol']])
