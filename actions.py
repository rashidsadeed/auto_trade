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