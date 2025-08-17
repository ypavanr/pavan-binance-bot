
import sys
import os
import logging
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
ORDER_TYPE_STOP = "STOP"

if not api_key or not api_secret:
    logging.error("BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.")
    sys.exit(1)

if len(sys.argv) < 6:
    logging.info("Usage: python advanced/stop_limit_orders.py <symbol> <side> <quantity> <stop_price> <limit_price>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    quantity = float(sys.argv[3])
    stop_price = float(sys.argv[4])
    limit_price = float(sys.argv[5])
except ValueError:
    logging.error("Error: Quantity, Stop Price, and Limit Price must be numbers.")
    sys.exit(1)

if side_str == 'BUY':
    side = SIDE_BUY
elif side_str == 'SELL':
    side = SIDE_SELL
else:
    logging.error("Error: Side must be 'BUY' or 'SELL'.")
    sys.exit(1)

try:
    bot = BasicBot(api_key, api_secret, testnet=True)
    client = bot.client
except Exception as e:
    logging.error(f"Failed to initialize Binance client: {e}")
    sys.exit(1)

try:
    logging.info(f"Placing a STOP-LIMIT {side_str} order for {quantity} {symbol}")
    logging.info(f"  - Stop Price: {stop_price}")
    logging.info(f"  - Limit Price: {limit_price}")

    order = client.futures_create_order(
        symbol=symbol,
        side=side,
        type=ORDER_TYPE_STOP,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=limit_price,
        stopPrice=stop_price
    )


    logging.info("Order placed successfully! ")
    logging.info(f"  - Order ID: {order.get('orderId')}")
    logging.info(f"  - Symbol: {order.get('symbol')}")
    logging.info(f"  - Side: {order.get('side')}")
    logging.info(f"  - Type: {order.get('type')}")
    logging.info(f"  - Status: {order.get('status')}")
    logging.info(f"  - Stop Price: {order.get('stopPrice')}")
    logging.info(f"  - Original Quantity: {order.get('origQty')}")

except BinanceAPIException as e:
    logging.error(f"Binance API Error (Code {e.code}): {e.message}")
except BinanceRequestException as e:
    logging.error(f"Binance Request Error: {e.message}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")