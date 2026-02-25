
import sys
import os
import pandas as pd
import ta
import time
from datetime import datetime
import requests

class Market:
    def get_klines(self, symbol, timeframe, limit=100):
        # 1. Try Binance
        try:
            pair = symbol.replace("/", "")
            # Binance intervals: 1h, 4h, 1d
            url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={timeframe}&limit={limit}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # [Open time, Open, High, Low, Close, Volume, ...]
                df = pd.DataFrame(data, columns=['ts', 'o', 'h', 'l', 'c', 'vol', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
                df = df[['ts', 'o', 'h', 'l', 'c', 'vol']]
                for col in ['ts', 'o', 'h', 'l', 'c', 'vol']:
                    df[col] = pd.to_numeric(df[col])
                print(f"✅ Fetched {timeframe} data from Binance")
                return df
        except Exception as e:
            print(f"⚠️ Binance failed: {e}")

        # 2. Try Gate.io as fallback
        try:
            pair = symbol.replace("/", "_") # ETH_USDT
            # Gate intervals: 1h, 4h, 1d
            url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={pair}&interval={timeframe}&limit={limit}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Gate.io usually returns [ts, volume, close, high, low, open, amount, is_closed]
                # We just need the first 6
                df = pd.DataFrame(data)
                # Take only first 6 columns regardless of how many returned
                df = df.iloc[:, :6]
                df.columns = ['ts', 'vol', 'c', 'h', 'l', 'o']
                df['ts'] = pd.to_numeric(df['ts']) * 1000
                for col in ['o', 'h', 'l', 'c', 'vol']:
                    df[col] = pd.to_numeric(df[col])
                print(f"✅ Fetched {timeframe} data from Gate.io")
                return df
        except Exception as e:
            print(f"⚠️ Gate.io failed: {e}")
        
        return None

def analyze_eth_technical():
    market = Market()
    symbol = "ETH/USDT"
    
    print(f"🔍 Fetching technical data for {symbol}...")
    
    timeframes = ['4h', '1d', '1w'] # Include Weekly for long-term support check
    results = {}
    
    for tf in timeframes:
        # For weekly, we might need more data to calculate moving averages
        limit = 200 if tf == '1w' else 100
        df = market.get_klines(symbol, tf, limit=limit)
        
        if df is None or df.empty:
            print(f"Failed to fetch {tf} data")
            continue
            
        current_price = df['c'].iloc[-1]
        
        # --- Indicators ---
        
        # 1. RSI (14)
        rsi_indicator = ta.momentum.RSIIndicator(close=df['c'], window=14)
        df['rsi'] = rsi_indicator.rsi()
        rsi = df['rsi'].iloc[-1]
        
        # 2. Bollinger Bands (20, 2)
        bb_indicator = ta.volatility.BollingerBands(close=df['c'], window=20, window_dev=2)
        df['bb_low'] = bb_indicator.bollinger_lband()
        bb_low = df['bb_low'].iloc[-1]
        
        # 3. MA 200 (Weekly/Daily is crucial for 1800 level)
        ma_200_indicator = ta.trend.SMAIndicator(close=df['c'], window=200)
        df['ma_200'] = ma_200_indicator.sma_indicator()
        ma_200 = df['ma_200'].iloc[-1]
        
        # 4. Support Levels (Local Lows)
        # Find local minima in the last 50 candles
        df['min_50'] = df['l'].rolling(window=50).min()
        recent_low = df['min_50'].iloc[-1]

        results[tf] = {
            "price": current_price,
            "rsi": rsi,
            "bb_low": bb_low,
            "ma_200": ma_200,
            "recent_low": recent_low
        }
        
    # --- Analysis Output ---
    print("\n📊 ETH/USDT Technical Analysis Summary:")
    
    current_price = results['1d']['price']
    print(f"Current Price: {current_price:.2f}")
    
    # Check probability of 1800
    target_1800 = 1800
    distance_pct = ((current_price - target_1800) / current_price) * 100
    
    print(f"\n📉 Distance to 1800: {distance_pct:.2f}% drop required")
    
    print("\n[Key Support Levels]")
    for tf, data in results.items():
        print(f"[{tf.upper()}]")
        print(f"  • RSI: {data['rsi']:.1f}")
        print(f"  • Bollinger Low: {data['bb_low']:.2f}")
        if not pd.isna(data['ma_200']):
            print(f"  • MA200: {data['ma_200']:.2f}")
        print(f"  • Recent Low (50 candles): {data['recent_low']:.2f}")

    # Judgment
    print("\n⚖️ Technical Verdict:")
    if current_price < 2000:
        print("CRITICAL: Price is already dangerously close to 1800 zone.")
    elif results['1d']['rsi'] < 30:
        print("Oversold on Daily. Bounce likely before further drop.")
    else:
        print("Neutral/Bearish structure.")

if __name__ == "__main__":
    analyze_eth_technical()
