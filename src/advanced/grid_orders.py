# advanced/grid_orders.py

import sys
import os
import logging
import time
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException

# Correctly set the path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.bot_client import BasicBot

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# --- API Key Loading ---
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

if not api_key or not api_secret:
    logging.error("BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.")
    sys.exit(1)

# --- Argument Parsing ---
if len(sys.argv) < 5:
    logging.info("Usage: python advanced/grid_orders.py <symbol> <lower_price> <upper_price> <num_grids> <quantity_per_grid>")
    sys.exit(1)

symbol = sys.argv[1].upper()
try:
    lower_price = float(sys.argv[2])
    upper_price = float(sys.argv[3])
    num_grids = int(sys.argv[4])
    quantity_per_grid = float(sys.argv[5])
except ValueError:
    logging.error("Error: All price and quantity arguments must be numbers.")
    sys.exit(1)

# --- Bot Initialization ---
try:
    bot = BasicBot(api_key, api_secret, testnet=True)
    client = bot.client
except Exception as e:
    logging.error(f"Failed to initialize Binance client: {e}")
    sys.exit(1)

# --- Grid Strategy Logic ---
def create_grid_orders(symbol, lower, upper, grids, quantity, client):
    """Calculates and places the initial grid of limit orders."""
    price_step = (upper - lower) / num_grids
    
    # Get the current market price to determine which side to place orders on
    # Get the current market price to determine which side to place orders on
    info = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(info['price'])

    
    orders = []
    
    for i in range(num_grids):
        grid_price = lower + (i + 1) * price_step
        
        # Place buy orders below current price, sell orders above
        if grid_price < current_price:
            side = SIDE_BUY
        else:
            side = SIDE_SELL
        
        try:
            order = client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=grid_price,
                timeInForce=TIME_IN_FORCE_GTC
            )
            orders.append(order)
            logging.info(f"Placed initial {side} order at {grid_price}. Order ID: {order['orderId']}")
        except BinanceAPIException as e:
            logging.error(f"API Error placing order at {grid_price}: {e.message}")
            continue

    return orders

def run_grid_strategy(orders, symbol, lower, upper, grids, quantity, client):
    """Monitors and replenishes grid orders."""
    order_ids = {o['orderId']: o for o in orders}
    
    logging.info("Grid trading strategy is now active. Monitoring for filled orders...")
    
    while True:
        try:
            # Get all open orders
            open_orders = client.futures_get_open_orders(symbol=symbol)
            current_open_ids = {o['orderId'] for o in open_orders}
            
            # Find filled orders by comparing open orders with our initial list
            filled_order_ids = set(order_ids.keys()) - current_open_ids

            if filled_order_ids:
                logging.info(f"Found {len(filled_order_ids)} filled orders.")
                for filled_id in filled_order_ids:
                    # Get details of the filled order
                    filled_order = client.futures_get_order(symbol=symbol, orderId=filled_id)
                    filled_price = float(filled_order['price'])
                    filled_side = filled_order['side']
                    
                    logging.info(f"Order ID {filled_id} ({filled_side} at {filled_price}) was filled.")
                    
                    # Determine the new order to place
                    if filled_side == SIDE_BUY:
                        # Buy filled -> place a new sell order one grid up
                        new_price = filled_price + ((upper - lower) / grids)
                        new_side = SIDE_SELL
                    else:
                        # Sell filled -> place a new buy order one grid down
                        new_price = filled_price - ((upper - lower) / grids)
                        new_side = SIDE_BUY

                    # Place the new order
                    if lower <= new_price <= upper:
                        new_order = client.futures_create_order(
                            symbol=symbol,
                            side=new_side,
                            type=ORDER_TYPE_LIMIT,
                            quantity=quantity,
                            price=new_price,
                            timeInForce=TIME_IN_FORCE_GTC
                        )
                        order_ids[new_order['orderId']] = new_order
                        logging.info(f"Placed new {new_side} order at {new_price}. ID: {new_order['orderId']}")
                    else:
                        logging.warning(f"New order price {new_price} is outside the grid range. Skipping.")
                
                # Update the list of active orders
                order_ids = {o['orderId']: o for o in open_orders}
                
            time.sleep(10) # Poll every 10 seconds

        except Exception as e:
            logging.error(f"An error occurred during monitoring: {e}")
            time.sleep(30) # Wait before retrying

# --- Main Execution ---
try:
    initial_orders = create_grid_orders(symbol, lower_price, upper_price, num_grids, quantity_per_grid, client)
    run_grid_strategy(initial_orders, symbol, lower_price, upper_price, num_grids, quantity_per_grid, client)

except BinanceAPIException as e:
    logging.error(f"Binance API Error (Code {e.code}): {e.message}")
except BinanceRequestException as e:
    logging.error(f"Binance Request Error: {e.message}")
except Exception as e:
    logging.error(f"An unexpected error occurred in the main process: {e}")