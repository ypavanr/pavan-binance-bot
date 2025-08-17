
import sys
import os
import logging
import time
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException

ORDER_TYPE_STOP_MARKET = "STOP_MARKET"
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

# --- CLI Args ---
if len(sys.argv) < 6:
    logging.info("Usage: python advanced/oco.py <symbol> <side> <quantity> <take_profit_price> <stop_loss_price>")
    sys.exit(1)

symbol = sys.argv[1].upper()
side_str = sys.argv[2].upper()
try:
    quantity = float(sys.argv[3])
    take_profit_price = float(sys.argv[4])
    stop_loss_price = float(sys.argv[5])
except ValueError:
    logging.error("Error: Quantity, Take Profit Price, and Stop Loss Price must be numbers.")
    sys.exit(1)

if side_str == 'BUY':
    take_profit_side = SIDE_SELL
    stop_loss_side = SIDE_SELL
elif side_str == 'SELL':
    take_profit_side = SIDE_BUY
    stop_loss_side = SIDE_BUY
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
    logging.info(f"Placing simulated OCO for {quantity} {symbol}")
    logging.info(f"  - Take-Profit Limit Price: {take_profit_price}")
    logging.info(f"  - Stop-Loss Trigger Price: {stop_loss_price}")

    tp_order = client.futures_create_order(
        symbol=symbol,
        side=take_profit_side,
        type=ORDER_TYPE_LIMIT,
        quantity=quantity,
        price=take_profit_price,
        timeInForce=TIME_IN_FORCE_GTC
    )
    logging.info("Take-Profit order placed successfully! ")
    logging.info(f"  - Order ID: {tp_order.get('orderId')}")

    sl_order = client.futures_create_order(
        symbol=symbol,
        side=stop_loss_side,
        type=ORDER_TYPE_STOP_MARKET,
        quantity=quantity,
        stopPrice=stop_loss_price
    )
    logging.info("Stop-Loss order placed successfully! ")
    logging.info(f"  - Order ID: {sl_order.get('orderId')}")

    logging.info("Simulated OCO orders are now active. Monitoring for fill status...")

    while True:
        tp_status = client.futures_get_order(symbol=symbol, orderId=tp_order.get('orderId'))['status']
        sl_status = client.futures_get_order(symbol=symbol, orderId=sl_order.get('orderId'))['status']

        if tp_status == 'FILLED':
            logging.info("✅ Take-Profit order filled! Canceling Stop-Loss order...")
            client.futures_cancel_order(symbol=symbol, orderId=sl_order.get('orderId'))
            logging.info("Simulated OCO strategy complete.")
            break
        
        if sl_status == 'FILLED':
            logging.info("❌ Stop-Loss order filled! Canceling Take-Profit order...")
            client.futures_cancel_order(symbol=symbol, orderId=tp_order.get('orderId'))
            logging.info("Simulated OCO strategy complete.")
            break
            
        time.sleep(5)  

except BinanceAPIException as e:
    logging.error(f"Binance API Error (Code {e.code}): {e.message}")
except BinanceRequestException as e:
    logging.error(f"Binance Request Error: {e.message}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
