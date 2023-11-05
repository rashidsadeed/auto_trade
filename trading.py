from actions import *
from strategies import *
from datetime import date
import datetime
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

agent = Actions(b_client)

while True:
    if collection.count_documents({}) > doc_len:
        new_data, latest_price = agent.get_data(collection)
        strategist = Strategist("BTCUSDT",new_data, agent)
        strategist.run(5, 12)
        doc_len+=1            