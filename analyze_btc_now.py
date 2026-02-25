
import sys
import os
import pandas as pd
import ta
import time
from datetime import datetime
import requests

# Add the project root to sys.path so we can import from okx_quant_system
sys.path.append(os.path.join(os.getcwd(), 'okx_quant_system'))

try:
    from market import Market
except ImportError:
    # If import fails, mock the Market class or just implement fetch_ohlcv directly
    class Market:
        def __init__(self):
            self.base_url = "https://www.okx.com"
        
        def get_klines(self, symbol, timeframe, limit=100):
            # Try Binance first
            try:
                # Map timeframe: Binance uses same format 1h, 4h, 1d
                pair = symbol.replace("/", "")
                url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={timeframe}&limit={limit}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # Binance: [Open time, Open, High, Low, Close, Volume, ...]
                    df = pd.DataFrame(data, columns=['ts', 'o', 'h', 'l', 'c', 'vol', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
                    df = df[['ts', 'o', 'h', 'l', 'c', 'vol']]
                    df['ts'] = pd.to_numeric(df['ts'])
                    df['o'] = pd.to_numeric(df['o'])
                    df['h'] = pd.to_numeric(df['h'])
                    df['l'] = pd.to_numeric(df['l'])
                    df['c'] = pd.to_numeric(df['c'])
                    df['vol'] = pd.to_numeric(df['vol'])
                    print(f"✅ Fetched {timeframe} data from Binance")
                    return df
            except Exception as e:
                print(f"⚠️ Binance failed: {e}")

            # Try Gate.io as fallback
            try:
                # Map symbol: BTC/USDT -> BTC_USDT
                pair = symbol.replace("/", "_")
                # Map timeframe: Gate uses 1h, 4h, 1d
                url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={pair}&interval={timeframe}&limit={limit}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # Gate.io returns variable columns sometimes, but first 6 are consistent:
                    # [timestamp, trading_volume, close_price, high_price, low_price, open_price]
                    # Create DF first without column names
                    df = pd.DataFrame(data)
                    # Take first 6 columns
                    df = df.iloc[:, :6]
                    df.columns = ['ts', 'vol', 'c', 'h', 'l', 'o']
                    
                    # Gate timestamp is in seconds, convert to ms to match others if needed, but relative order is fine
                    df['ts'] = pd.to_numeric(df['ts']) * 1000 
                    df['o'] = pd.to_numeric(df['o'])
                    df['h'] = pd.to_numeric(df['h'])
                    df['l'] = pd.to_numeric(df['l'])
                    df['c'] = pd.to_numeric(df['c'])
                    df['vol'] = pd.to_numeric(df['vol'])
                    print(f"✅ Fetched {timeframe} data from Gate.io")
                    return df
            except Exception as e:
                print(f"⚠️ Gate.io failed: {e}")
            
            return None

def analyze_btc_technical():
    market = Market()
    symbol = "BTC/USDT"
    
    print(f"🔍 Fetching technical data for {symbol}...")
    
    timeframes = ['1h', '4h', '1d']
    results = {}
    
    for tf in timeframes:
        df = market.get_klines(symbol, tf, limit=100)
        if df is None or df.empty:
            print(f"Failed to fetch {tf} data")
            continue
            
        current_price = df['c'].iloc[-1]
        
        # Calculate Indicators using 'ta' library
        
        # 1. RSI
        rsi_indicator = ta.momentum.RSIIndicator(close=df['c'], window=14)
        df['rsi'] = rsi_indicator.rsi()
        rsi = df['rsi'].iloc[-1]
        
        # 2. MACD
        macd_indicator = ta.trend.MACD(close=df['c'])
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_diff'] = macd_indicator.macd_diff()
        
        macd_val = df['macd'].iloc[-1]
        macd_signal = df['macd_signal'].iloc[-1]
        macd_hist = df['macd_diff'].iloc[-1]
        
        # 3. EMA Trends
        ema_20_indicator = ta.trend.EMAIndicator(close=df['c'], window=20)
        df['ema_20'] = ema_20_indicator.ema_indicator()
        
        ema_50_indicator = ta.trend.EMAIndicator(close=df['c'], window=50)
        df['ema_50'] = ema_50_indicator.ema_indicator()
        
        ema_200_indicator = ta.trend.EMAIndicator(close=df['c'], window=200)
        df['ema_200'] = ema_200_indicator.ema_indicator()
        
        ema_20 = df['ema_20'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        ema_200 = df['ema_200'].iloc[-1] if not pd.isna(df['ema_200'].iloc[-1]) else 0
        
        # 4. Bollinger Bands
        bb_indicator = ta.volatility.BollingerBands(close=df['c'], window=20, window_dev=2)
        df['bb_high'] = bb_indicator.bollinger_hband()
        df['bb_low'] = bb_indicator.bollinger_lband()
        
        bb_upper = df['bb_high'].iloc[-1]
        bb_lower = df['bb_low'].iloc[-1]
        
        # Determine Trend
        trend = "Neutral"
        if current_price > ema_20 > ema_50:
            trend = "Bullish"
        elif current_price < ema_20 < ema_50:
            trend = "Bearish"
            
        # Determine Momentum
        momentum = "Neutral"
        if rsi > 70: momentum = "Overbought"
        elif rsi < 30: momentum = "Oversold"
        elif macd_val > macd_signal: momentum = "Bullish Momentum"
        elif macd_val < macd_signal: momentum = "Bearish Momentum"
        
        results[tf] = {
            "price": current_price,
            "rsi": rsi,
            "macd_hist": macd_hist,
            "trend": trend,
            "momentum": momentum,
            "support": bb_lower,
            "resistance": bb_upper,
            "ema_200": ema_200
        }
        
    return results

if __name__ == "__main__":
    data = analyze_btc_technical()
    print("\n📊 Technical Analysis Summary:")
    for tf, res in data.items():
        print(f"\n[{tf.upper()} Timeframe] Price: {res['price']}")
        print(f"  • Trend: {res['trend']}")
        print(f"  • Momentum: {res['momentum']} (RSI: {res['rsi']:.1f})")
        print(f"  • MACD Histogram: {res['macd_hist']:.2f} ({'Bullish' if res['macd_hist']>0 else 'Bearish'})")
        print(f"  • Support (BB Lower): {res['support']:.2f}")
        print(f"  • Resistance (BB Upper): {res['resistance']:.2f}")
