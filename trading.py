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

class Strategist:
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

def get_data(collection):
    #data from mongoDB to pandas
    pandas_data = pd.DataFrame(list(collection.find()))
    #get latest entry
    latest_entry = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    return pandas_data, latest_entry





while True:
    if collection.count_documents({}) > doc_len:
        new_data, latest_price = get_data(collection)
        strategist = Strategist(new_data)
        strategist.Momentum_strategy(3)
        doc_len+=1
    
            