from market import MarketData
from config import SYMBOL

try:
    m = MarketData()
    print("Testing Ticker...")
    ticker = m.get_ticker(SYMBOL)
    print(f"Ticker: {ticker['last']}")
    
    print("Testing OHLCV...")
    df = m.fetch_ohlcv(SYMBOL)
    print(df.tail())
except Exception as e:
    print(f"Error: {e}")
