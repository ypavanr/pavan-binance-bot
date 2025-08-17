visit "https://testnet.binancefuture.com/en/futures/BTCUSDT". Create an account and get your API key and API secret.

clone this repository from the github url using "git clone <URL>" command.

execute the following command to set your api environment variables.

export BINANCE_API_SECRET="your api secret"  
export BINANCE_API_KEY="your api key"

the above command is for for mac/linux. for windows(cmd) you must use: 
set BINANCE_API_SECRET="your api secret"  
set BINANCE_API_KEY="your api key"

after entering the root directory, execute the following commands to setup virtual environment:
python -m venv myenv
source venv/bin/activate (myenv\Scripts\activate.bat for windows cmd)

now execute the following command to install all the required dependencies:
pip install requirements.txt


market orders example run: python src/market_orders.py BTCUSDT BUY 0.01

limit orders example run: python src/limit_orders.py BTCUSDT BUY 0.01 28000.00


stop limit order example run: 
cd src
python advanced/stop_limit_order.py USDT-M SELL 0.01 59000 58900


twap example run: 
cd src
python advanced/twap.py BTCUSDT BUY 0.5 30 


oco example run: 
cd src
python advanced/oco.py BTCUSDT SELL 0.01 65000 55000

