# src/bot_client.py

from binance.client import Client

class BasicBot:
   
    def __init__(self, api_key, api_secret, testnet=True):
       
        self.client = Client(api_key, api_secret, testnet=testnet)