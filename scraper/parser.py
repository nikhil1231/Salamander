import requests
from bs4 import BeautifulSoup

class Coin:
  def __init__(self, row_data):
    self.name = self.__parse_name(row_data)
    self.ticker = self.__parse_ticker(row_data)
    self.chain = self.__parse_chain(row_data)

  def __parse_name(self, row_data):
    return row_data.find('td', class_='py-0 coin-name')['data-sort']

  def __parse_ticker(self, row_data):
    return row_data.find('td', class_='py-0 coin-name').find('a', class_='d-lg-none font-bold').contents[0].replace('\n', '').lower()

  def __parse_chain(self, row_data):
    return row_data.find('td', class_='coin-name tw-text-right')['data-sort']

def get_parsed_recent_coins():
  r = requests.get('https://www.coingecko.com/en/coins/recently_added')
  soup = BeautifulSoup(r.content, "html.parser")
  main_table = soup.find("table", class_="sort table mb-0 text-sm text-lg-normal table-scrollable")

  return [Coin(row_data) for row_data in main_table.find_all("tr")[1:]]
