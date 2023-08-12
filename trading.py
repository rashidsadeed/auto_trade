from ast import Num
from datetime import date
from operator import ne
from pydoc import doc
import re
from pymongo import MongoClient
import pymongo
import pandas as pd
import datetime
import numpy as np

client = MongoClient()
collection = client.OHLC.test
doc_len = collection.count_documents({})

class Actions:

    def get_data(self, collection):
        #data from mongoDB to pandas
        pandas_data = pd.DataFrame(list(collection.find()))
        #get latest entry
        latest_entry = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        return pandas_data, latest_entry

    def get_date_price(self, bar):
        date = str(self.data.index[bar])[:10]
        price = self.data.Close.iloc[bar]
        return date, price

    def place_sell_order(self, bar, units = None, amount=None):
        date, price = self.get_date_price(bar)
        if units is None:
            units = int(amount/price)
        self.amount += (units * price) * (1-self.ptc) - self.ftc
        
        self.units -= units
        self.trades += 1
        if self.verbose:
            print(f"{date} | selling {units} units at {price:.2f}")
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def place_buy_order(self, bar, units=None, amount=None):
        date, price = self.get_date_price(bar)
        
        if units is None:
            units = int(amount/price)
        self.amount -= (units * price) * (1+self.ptc) + self.ftc
        
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f"{date} | selling {units} units at {price:.2f}")
            
            self.print_balance(bar)
            self.print_net_wealth(bar)


    def set_stop_loss():
        print("stop_loss")

    def close_out(self, bar):
        date, price = self.get_date_price(bar)
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        if self.verbose:
            print(f"{date} | inventory {self.units} units at {price:.2f}")
            print("=" * 55)
        
        print(f"Final balance  [$ ]{self.amount:.2f}")
        perf = ((self.amount - self.initial_amount)/self.initial_amount * 100)
        print(f"Net performance [%] {perf:.2f}")
        print(f"Trades executed [#] {self.trades:.2f}")
        print("=" * 55)

class Strategist(Actions):
    def __init__(self,data, active_strat="SMA_strategy"):
        self.active_strat = active_strat
        self.data = data

    def SMA_strategy(self, SMA1, SMA2):
        return "somwthing"

    def EMA_strategy(self):
        return "something"

    def Momentum_strategy(self, momentum):
        global doc_len
        min_len = momentum + 1
        if collection.count_documents({}) > doc_len:
            self.data["returns"] = np.log(self.data["close"]/self.data["close"].shift(1))
            if len(self.data["close"]) > min_len:
                self.data["momentum"] = np.sign(self.data["returns"].rolling(momentum).mean())
                print("\n" + "=" * 51)
                print(f"NEW SIGNAL | {datetime.datetime.now()}")
                print("=" * 51)
                print(self.data.iloc[:-1].tail())
                if self.data["momentum"].iloc[-2] == -1.0:
                    print("long position.")
                    print("WE SUPPOSEDLY bought here")
                
                elif self.data["momentum"].iloc[-2] == -1.0:
                    print("short position here")
                    print("WE SUPPOESDLY sold here")
            
    def run(self):
        if self.active_strat == "SMA_strategy":
            self.SMA_strategy()
        elif self.active_strat == "EMA_strategy":
            self.EMA_strategy()
        elif self.active_strat == "Momentum_strategy":
            self.Momentum_strategy(3)

agent = Actions()
while True:
    if collection.count_documents({}) > doc_len:
        new_data, latest_price = agent.get_data(collection)
        strategist = Strategist(new_data)
        strategist.Momentum_strategy(3)
        doc_len+=1
    
            