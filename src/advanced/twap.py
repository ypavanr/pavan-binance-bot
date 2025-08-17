# advanced/twap_orders.py

import sys
import os
import logging
import time
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.bot_client import BasicBot

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

if len(sys.argv) < 5:
    logging.info("Usage: python advanced/twap_orders.py <symbol> <side> <total_quantity> <duration_minutes>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    total_quantity = float(sys.argv[3])
    duration_minutes = float(sys.argv[4])
except ValueError:
    logging.error("Error: Total quantity and duration must be numbers.")
    sys.exit(1)

if side_str == 'BUY':
    side = SIDE_BUY
elif side_str == 'SELL':
    side = SIDE_SELL
else:
    logging.error("Error: Side must be 'BUY' or 'SELL'.")
    sys.exit(1)


NUMBER_OF_SUB_ORDERS = 10
delay_seconds = (duration_minutes * 60) / NUMBER_OF_SUB_ORDERS
sub_order_quantity = total_quantity / NUMBER_OF_SUB_ORDERS

try:
    bot = BasicBot(api_key, api_secret, testnet=True)
    client = bot.client
except Exception as e:
    logging.error(f"Failed to initialize Binance client: {e}")
    sys.exit(1)

try:
    logging.info(f"Starting TWAP order for {total_quantity} {symbol} over {duration_minutes} minutes.")
    logging.info(f"Splitting into {NUMBER_OF_SUB_ORDERS} orders of {sub_order_quantity} each, with a delay of {delay_seconds:.2f} seconds.")

    for i in range(NUMBER_OF_SUB_ORDERS):
        logging.info(f"Placing sub-order {i+1}/{NUMBER_OF_SUB_ORDERS}")
        
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=sub_order_quantity
        )
        
        logging.info("Sub-order placed successfully! ")
        logging.info(f"  - Order ID: {order.get('orderId')}")
        logging.info(f"  - Status: {order.get('status')}")
        logging.info(f"  - Executed Quantity: {order.get('executedQty')}")
        
        if i < NUMBER_OF_SUB_ORDERS - 1:
            logging.info(f"Waiting for {delay_seconds:.2f} seconds before next order-")
            time.sleep(delay_seconds)

    logging.info("TWAP order strategy completed. All sub-orders have been placed.")

except BinanceAPIException as e:
    logging.error(f"Binance API Error (Code {e.code}): {e.message}")
except BinanceRequestException as e:
    logging.error(f"Binance Request Error: {e.message}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")