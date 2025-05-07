from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import glob
import time
import os


class LookupStock:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--log-level=3")  # Suppresses most logs (INFO, WARNING, etc.)
        self.service = Service(log_path='NUL')
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.stocks = []
        self.collected_data = {}

    def add_stocks_to_track(self, stocks):
        if isinstance(stocks, list):
            for stock in stocks:
                self.__add_stock_to_track(stock)
        elif isinstance(stocks, str):
            self.__add_stock_to_track(stock)
        else:
            raise TypeError("Error: Invalid stocks type. Please pass argument of type list or str.")            

    def __add_stock_to_track(self, symbol: str):
        symbol = symbol.upper()
        if symbol in self.stocks:
            raise Exception(f"Error: Symbol of value {symbol} already in tracking list.")

        self.stocks.append(symbol)
        self.collected_data[symbol] = [[],[]]

        output_path = os.path.join(self.basedir, "quotes", f"{symbol}.csv")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write("symbol, name, price, datetime\n")

    def remove_stock_to_track(self, symbol: str, delete_history=False):
        symbol = symbol.upper()
        if symbol not in self.stocks:
            raise Exception(f"Error: No symbol of value '{symbol}' in tracking list to remove.")
        self.stocks.remove(symbol)

        if delete_history:
            path = os.path.join(self.basedir, "quotes", f"{symbol}.csv")
            try:
                os.remove(path)
            except FileNotFoundError:
                print(f"File not found: {path}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")

    def collect_data_loop(self, interval=300):
        try:
            while(True):
                print(f"- [{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] Saving stocks data...")
                self.__save_stocks_data()
                print(f"+ [{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}] Done saving stocks data")
                time.sleep(interval)
        except KeyboardInterrupt:
            return


    def __save_stocks_data(self):
        lookup_data = []

        self.browser = webdriver.Chrome(service=self.service, options=self.chrome_options)

        for symbol in self.stocks:
            lookup_data.append(
                self.__lookup(symbol)
            )


        self.browser.quit()

        self.__save_results(lookup_data)

    def __lookup(self, symbol: str):
        self.browser.get(f'https://finance.yahoo.com/quote/{symbol}/')

        price = self.browser.find_element(By.XPATH, '//*[@data-testid="qsp-price"]').text
        name = self.browser.find_element(By.XPATH, '//*[@data-testid="quote-hdr"]/div[1]//h1').text

        price = self.__format_price(price)
        name = self.__format_name(name)

        return {
            'symbol': symbol,
            'price': price,
            'name': name
        }
    
    def __save_results(self, lookups: list):
        for lookup in lookups:
            path = os.path.join(self.basedir, "quotes", f"{lookup['symbol']}.csv")
            current_date = datetime.now()

            self.collected_data[lookup['symbol']][0].append(
                lookup['price']
            )
            self.collected_data[lookup['symbol']][1].append(
                current_date.replace(second=0, microsecond=0)
            )

            with open(path, 'a', encoding='utf-8') as file:
                file.write(f"{lookup['symbol']},{lookup['name']},{lookup['price']},{current_date}\n")
        
    def __format_price(self, price: str):
        try:
            price = float(price)
        except:
            print(f"Error converting price '{price}' to float")

        return price
    
    def __format_name(self, name:str):
        return name.rsplit("(", maxsplit=1)[0].strip()
    
    def clear_history(self):
        self.__clear_quotes_history()
        self.__clear_graphs_history()

    def __clear_quotes_history(self):
        quote_paths = glob.glob(os.path.join(self.basedir, "quotes", "*.csv"))
        self.__delete_paths(quote_paths)

    def __clear_graphs_history(self):
        graph_paths = glob.glob(os.path.join(self.basedir, "graphs", "*.png"))
        self.__delete_paths(graph_paths)

    def __delete_paths(self, paths):
        for path in paths:
            try:
                os.remove(path)
            except FileNotFoundError:
                print(f"File not found: {path}")
            except Exception as e:
                print(f"Error deleting {path}: {e}")


    def generate_results_graphs(self):
        for symbol in self.collected_data:
            prices = np.array(self.collected_data[symbol][0])
            dates = np.array(self.collected_data[symbol][1])

            plt.figure(figsize=(10, 5))
            plt.plot(dates, prices)
            
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.gcf().autofmt_xdate()
            plt.xlabel("Time")
            plt.ylabel("Stock Price")
            plt.title(f"{symbol} Price Over Time")
            plt.ylim(min(prices) - 1, max(prices) + 1)

            graph_path = os.path.join(self.basedir, "graphs", f"{symbol}.png")
            plt.savefig(graph_path)
            plt.close()
            



if __name__ == '__main__':
    stocks = ['NVDA', 'AMD', 'GOOGL', 'PLTR', 'LCID']
    stock_bot = LookupStock()

    stock_bot.clear_history()
    stock_bot.add_stocks_to_track(stocks)

    stock_bot.collect_data_loop(interval=300)

    stock_bot.generate_results_graphs()
        

