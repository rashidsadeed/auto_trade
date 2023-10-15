from . import actions, strategies
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
import os
from dotenv import load_dotenv

#loading binance API keys 
load_dotenv(override=True)
api_key = os.getenv("api_key")
secret_key = os.getenv("secret_key")
#creating client for Binance
b_client = Client(api_key,secret_key)
#setting up mongoDB
client = MongoClient()
collection = client.OHLC.test
doc_len = collection.count_documents({})

agent = actions.Actions(b_client)

while True:
    if collection.count_documents({}) > doc_len:
        new_data, latest_price = agent.get_data(collection)
        strategist = strategies.Strategist("BTCUSDT",new_data, agent)
        strategist.run(25, 50)
        doc_len+=1            