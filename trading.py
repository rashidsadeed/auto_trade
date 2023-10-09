from datetime import date
from pymongo import MongoClient
import pymongo
import pandas as pd
import pandas_ta as pt
import talib as tb
import datetime
import numpy as np
from binance.client import Client
from binance.enums import *

b_client = Client("api key", "private key")
client = MongoClient()
collection = client.OHLC.test
doc_len = collection.count_documents({})


class Actions:
    def __init__(self, client):
        self.client = client

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
        
        """binance API sell order"""
        order = client.create_order(symbol=bar, side="SELL", type="MARKET", quantity=units)
        """to be sure of the syntax first without staking any money 
        be sure to use create_test_order function first"""
        
        #self.amount += (units * price) * (1-self.ptc) - self.ftc
        print(order)

        
        # refine this part to work in real-time
        """get this information live from binance"""
        #####client.get_asset_balance(asset=bar)
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

        """binance API BUY  order"""
        order = client.create_order(symbol=bar, side="SELL", type="MARKET", quantity=units)
        #self.amount -= (units * price) * (1+self.ptc) + self.ftc
        print(order)


        #refine this part to work in real-time
        """have to get this information live from binance"""
        #####client.get_asset_balance(asset=bar)
        self.units += units
        self.trades += 1
        if self.verbose:
            print(f"{date} | selling {units} units at {price:.2f}")
            
            self.print_balance(bar)
            self.print_net_wealth(bar)

    def set_stop_loss(self, bar, Sprice, SLprice):
        try:
            
            order = client.create_oco_order(
                symbol=bar,
                side='SELL',
                quantity=100,
                price=250,
                stopPrice=Sprice,
                stopLimitPrice=SLprice,
                stopLimitTimeInForce='GTC')

            print(order)

        except BinanceAPIException as e:
            # error handling goes here
            print(e)

    ###check this code again to make sense of it and implement it in binance API terms
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
    def __init__(self,symbol, data, agent, active_strat="SMA_strategy", position=0):
        self.active_strat = active_strat
        self.position = position
        self.data = data
        self.open = data["open"]
        self.high = data["high"]
        self.low = data["low"]
        self.close = data["close"]
        self.agent = agent
        self.symbol = symbol


    def SMA_strategy(self, symbol, SMA1, SMA2):
        """SMA1 should be smaller than SMA2"""
        self.data[f"SMA_{SMA1}"] = pt.sma(self.close, length=SMA1)
        self.data[f"SMA_{SMA2}"] = pt.sma(self.close, length=SMA2)

        for bar in range(SMA2, len(self.data)):
            #find a way to implement the position problem in the general outcome function
            if self.position == 0:
                if self.data[f"SMA_{SMA1}"].iloc[bar] > self.data[f"SMA_{SMA2}"].iloc[bar]:
                    self.position = 1
                    return "buy", symbol
            
            elif self.position == 1:
                if self.data[f"SMA_{SMA1}"] < self.data[f"SMA_{SMA2}"]:
                    self.position = 0
                    return "sell", symbol
    
    def EMA_strategy(self, symbol, EMA1, EMA2):
        self.data[f"EMA_{EMA1}"] = pt.sma(self.close, length=EMA1)
        self.data[f"EMA_{EMA2}"] = pt.sma(self.close, length=EMA2) 
        for bar in range(EMA2, len(self.data)): 
            if self.data[f"EMA_{EMA1}"].iloc[bar] > self.data[f"EMA_{EMA2}"].iloc[bar]:
                return "buy", symbol
            elif self.data[f"EMA_{EMA1}"].iloc[bar] < self.data[f"EMA_{EMA2}"].iloc[bar]:
                return "sell", symbol

    "needs refining"
    def MACD_stochastic_strategy(self,symbol, stoch_fast, stock_slow, macd_fast, macd_slow, macd_signal):  
        self.data[["STOCHk", "STOCHd"]] = pt.stoch(self.high, self.low, self.close ,k=stoch_fast, d=stock_slow, talib=True)
        self.data[["MACD", 'MACDh', "MACDs"]] = pt.macd(self.close, fast=macd_fast, slow=macd_slow, signal=macd_signal)
        for bar in range(SMA2, len(self.data)):
            if self.data["MACD"].iloc[bar] > self.data["MACDh"].iloc[bar]:
                """this should be goes below 20 and immediatly comes above"""
                if self.data["STOCHk"].iloc[bar] < 20:
                    stage_1 = True
                    while stage_1:
                        if self.data["STOCHk"].iloc[bar] > 20:
                            stage_1 = False
                            return "buy", symbol
            elif self.data["MACD"].iloc[bar] < self.data["MACDh"].iloc[bar]:
                """this should be goes above 80 and then comes below after immediately"""
                if self.data["STOCHk"].iloc[bar] > 80:
                    stage_1 = True
                    while stage_1:
                        if self.data["STOCHk"].iloc[bar] < 80:
                            return "sell", symbol

    ###https://www.brokerxplorer.com/article/the-ultimate-3-ema-crossover-strategy-revealed-1856
    ###this staretegy is highly sketchycreate
    def triple_EMA_crossover(self, EMA1=10, EMA2=30, EMA3=50):
        #first you should create the EMAs in this part
        #
        #
        #

        if self.data["close"] > EMA1 and self.data["close"] > EMA2 and self.data["close"] > EMA3:
            #take action
            print("uptrend and rising momentum")
        elif self.data["close"] < EMA1 and self.data["close"] < EMA2 and self.data["close"] < EMA3:
            #take action
            print("downtrend and falling momentum")
        elif EMA3 > EMA2 and EMA3 > EMA1:
            #take action
            print("market has lost short-term momentum")
        elif self.data["close"] < EMA3:
            #take action
            print("reversal from long-term uptrend into a downtrend")
    
        if EMA2 > EMA3 and EMA1 > EMA2:
            #take action
            print("Long position")
        
        if EMA2 < EMA3 and EMA1 < EMA2:
            #take action
            print("Short position")

        if EMA2 < EMA3 and EMA1 > EMA2:
            #take action
            print("longer-term downtrend is potentially reversing into a longer-term uptrend")

        if EMA2 > EMA3 and EMA1 < EMA2:
            #take action
            print("longer-term uptrend is reversing into a longer-term downtrend")


    def Momentum_strategy(self, bar, momentum):
        global doc_len
        min_len = momentum + 1
        if collection.count_documents({}) > doc_len:
            self.data["returns"] = np.log(self.close/self.close.shift(1))
            if len(self.close) > min_len:
                self.data["momentum"] = np.sign(self.data["returns"].rolling(momentum).mean())
                print("\n" + "=" * 51)
                print(f"NEW SIGNAL | {datetime.datetime.now()}")
                print("=" * 51)
                print(self.data.iloc[:-1].tail())
                if self.data["momentum"].iloc[-2] == -1.0:
                    print("long position.")
                    return "buy", bar
                
                elif self.data["momentum"].iloc[-2] == -1.0:
                    print("short position here")
                    return "sell", bar
            
    def run(self, SMA1, SMA2):
        match self.active_strat:
            case "SMA_strategy":
                result, asset = self.SMA_strategy(self.symbol, SMA1, SMA2)
                if result == "buy":
                    self.agent.place_buy_order(asset)
                elif result == "sell":
                    self.agent.place_sell_order(asset)

        ###### You have to insert all the other strategies you have in here ########
                
        #if self.active_strat == "SMA_strategy":
        #    self.SMA_strategy()
        #elif self.active_strat == "EMA_strategy":
        #    self.EMA_strategy()
        #elif self.active_strat == "Momentum_strategy":
        #    self.Momentum_strategy(3)

def trade_calc(position=False):
    if not position:
        #here you insert the algorithm for the trade, and then...i.e if the combination of strategies you choose return "buy"
        position = True
        agent.place_buy_order
    elif position:
        position = False
        agent.place_sell_order    
    

agent = Actions(b_client)


while True:
    if collection.count_documents({}) > doc_len:
        new_data, latest_price = agent.get_data(collection)
        strategist = Strategist("BTCUSDT",new_data, agent)
        strategist.run(25, 50)
        doc_len+=1
    
            