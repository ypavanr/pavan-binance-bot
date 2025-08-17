
import sys
import os
import logging
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),  
        logging.StreamHandler()         
    ]
)

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

if not api_key or not api_secret:
    logging.error("BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.")
    sys.exit(1)

if len(sys.argv) < 4:
    logging.info("Usage: python src/market_orders.py <symbol> <side> <quantity>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    quantity = float(sys.argv[3])
except ValueError:
    logging.error("Error: Quantity must be a number.")
    sys.exit(1)

if side_str == 'BUY':
    side = SIDE_BUY
elif side_str == 'SELL':
    side = SIDE_SELL
else:
    logging.error("Error: Side must be 'BUY' or 'SELL'.")
    sys.exit(1)

client = Client(api_key, api_secret, testnet=True)

try:
    logging.info(f"Placing a MARKET {side_str} order for {quantity} {symbol}")
    
    order = client.futures_create_order(
        symbol=symbol,
        side=side,
        type=ORDER_TYPE_MARKET,
        quantity=quantity
    )

    logging.info("Order placed successfully! ")
    logging.info(f"  - Order ID: {order['orderId']}")
    logging.info(f"  - Symbol: {order['symbol']}")
    logging.info(f"  - Side: {order['side']}")
    logging.info(f"  - Type: {order['type']}")
    logging.info(f"  - Status: {order['status']}")
    
 
    logging.info(f"  - Original Quantity: {order['origQty']}")
    logging.info(f"  - Executed Quantity: {order['executedQty']}")

except BinanceAPIException as e:
    logging.error(f"Binance API Error (Code {e.code}): {e.message}")
except BinanceRequestException as e:
    logging.error(f"Binance Request Error: {e.message}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")