

import sys
from binance.client import Client
from binance.enums import *
import os

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

if len(sys.argv) < 4:
    print("Usage: python src/market_orders.py <symbol> <side> <quantity>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    quantity = float(sys.argv[3])
except ValueError:
    print("Error: Quantity must be a number.")
    sys.exit(1)

if side_str == 'BUY':
    side = SIDE_BUY
elif side_str == 'SELL':
    side = SIDE_SELL
else:
    print("Error: Side must be 'BUY' or 'SELL'.")
    sys.exit(1)

client = Client(api_key, api_secret, testnet=True)

try:
    print(f"Placing a MARKET {side_str} order for {quantity} {symbol}...")
    
    order = client.futures_create_order(
        symbol=symbol,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=quantity
    )

    print("Order placed successfully:")
    print(order)

except Exception as e:
    print(f"An error occurred: {e}")