
import sys
import os
from binance.client import Client
from binance.enums import *

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

if not api_key or not api_secret:
    print("Error: BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.")
    sys.exit(1)

if len(sys.argv) < 5:
    print("Usage: python src/limit_orders.py <symbol> <side> <quantity> <price>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    quantity = float(sys.argv[3])
    price = float(sys.argv[4])
except ValueError:
    print("Error: Quantity and Price must be numbers.")
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
    print(f"Placing a LIMIT {side_str} order for {quantity} {symbol} at {price}...")
    
    order = client.futures_create_order(
        symbol=symbol,
        side=side,
        type=ORDER_TYPE_LIMIT, 
        timeInForce=TIME_IN_FORCE_GTC, 
        quantity=quantity,
        price=price 
    )

    print("Order placed successfully:")
    print(order)

except Exception as e:
    print(f"An error occurred: {e}")