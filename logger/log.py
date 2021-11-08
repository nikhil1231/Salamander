import csv
from datetime import datetime

LOG_File = './data/log.csv'

def log(_type, token, chain, balance):
  with open(LOG_File, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
      datetime.now(),
      _type,
      token,
      chain,
      balance
    ])