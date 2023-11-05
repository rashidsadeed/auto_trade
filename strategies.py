import pandas_ta as pt
import talib as tb

class Strategist():
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


    def SMA_strategy(self, SMA1, SMA2):
        """SMA1 should be smaller than SMA2"""
        self.data[f"SMA_{SMA1}"] = pt.sma(self.close, length=SMA1)
        self.data[f"SMA_{SMA2}"] = pt.sma(self.close, length=SMA2)

        for bar in range(SMA2, len(self.data)):
            #find a way to implement the position problem in the general outcome function
            if self.position == 0:
                if self.data[f"SMA_{SMA1}"].iloc[bar] > self.data[f"SMA_{SMA2}"].iloc[bar]:
                    self.position = 1
                    return("buy", self.symbol)
            
            elif self.position == 1:
                if self.data[f"SMA_{SMA1}"] < self.data[f"SMA_{SMA2}"]:
                    self.position = 0
                    return("sell", self.symbol)
    
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
        #match self.active_strat:
        #    case "SMA_strategy":
        result, asset = self.SMA_strategy(SMA1, SMA2)
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