import websocket
from websocket._app import WebSocketApp as WBSA
import json
from pymongo import MongoClient
import pandas as pd
from datetime import datetime


class Logger:
    def __init__(self, interval, collection):
        """websocket connection to binance to get live data"""
        self.socket = f"wss://stream.binance.com:9443/ws/btcusdt@kline_{interval}"
        #MongoDB collection
        self.collection = collection
        #pandas DataFrame
        #self.df = df

   # def historical_data(self):
        #h_data = 




    def on_message(self, ws, message):
        data = json.loads(message)["k"]
        #check if the canlle is done to get the final OHLC data
        is_candle_closed = data["x"]
        post = {
        'open_time' : data["t"],
        'close_time' : data["T"],
        "time" : datetime.now(),
        'open' : float(data["o"]),
        'high' : float(data["h"]),
        'low' : float(data["l"]),
        'close' : float(data["c"]),
        'volume' : float(data["v"])
        }
        
        #insert data into MongoDB and the dataframe at the same time
        if is_candle_closed:
            print("loading...")
            self.collection.insert_one(post)
            print(post.open)
          
            #self.df.loc[len(self.df)] = post
        

        #remove old data from the dataframe to prevent high and unneccesary data consumption
        #if len(pand_data) > 500:
        #    pand_data = pand_data.iloc[-300:]

    def on_close(self, ws):
        print("the Connection is terminated")
        print(self.df)


    def fetch_data(self):
        ws =  WBSA(self.socket, on_message=self.on_message, on_close = self.on_close)
        ws.run_forever()


client = MongoClient()
collection = client.OHLC.test


minute = Logger("1m", collection)
minute.fetch_data()
