from trader import bsc
from scraper.new_coins import get_new_coins
import config
import threading
import schedule
import time

cfg = config.Config("config.ini")

DEV = cfg.get("dev")
REFRESH_TIMEOUT = 1
BNB_AMOUNT = cfg.get("trade_value") / 600

def start_scheduler(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def approve_token(token):
  bsc.approve_token(token, cfg.get('private'), dev=DEV)
  return schedule.CancelJob

def sell_token(token, ratio):
  bsc.sell_token(token, cfg.get("private"), ratio=ratio, dev=DEV)
  return schedule.CancelJob

def execute_strategy(token):
  bsc.buy_token(token, BNB_AMOUNT, cfg.get("private"), dev=DEV)

  schedule.every(30).seconds.do(approve_token, token=token)

  schedule.every(30).minutes.do(sell_token, token=token, ratio=1.0)

def check_new_coins(max_coins=1, initial=False):
  new_coins = get_new_coins(chains=['BSC'], max_coins=max_coins)

  if len(new_coins) == 0 or initial:
    return

  for new_coin in new_coins:
    execute_strategy(new_coin)


if __name__ == '__main__':
  start_scheduler()

  check_new_coins(initial=True)

  schedule.every(REFRESH_TIMEOUT).seconds.do(check_new_coins)
