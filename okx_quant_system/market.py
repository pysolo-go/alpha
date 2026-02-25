import requests
import pandas as pd
import time
from config import *

class MarketData:
    def __init__(self):
        self.base_url = "https://www.okx.com"
        
    def get_ticker(self, symbol):
        """获取最新行情"""
        # Symbol format: BTC/USDT:USDT -> BTC-USDT-SWAP (for OKX API)
        instId = symbol.replace("/", "-").replace(":USDT", "-SWAP")
        if "SWAP" not in instId and "USDT" in instId:
             instId = instId + "-SWAP" # Default to swap if not specified

        url = f"{self.base_url}/api/v5/market/ticker?instId={instId}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data['code'] == '0' and data['data']:
                return {
                    'last': float(data['data'][0]['last']),
                    'vol24h': float(data['data'][0]['volCcy24h'])
                }
            return None
        except Exception as e:
            print(f"❌ 获取行情失败: {e}")
            return None

    def fetch_ohlcv(self, symbol, timeframe='15m', limit=100):
        """获取 K 线数据并计算指标"""
        # Symbol format conversion
        instId = symbol.replace("/", "-").replace(":USDT", "-SWAP")
        if "SWAP" not in instId and "USDT" in instId:
             instId = instId + "-SWAP"

        # Timeframe conversion (15m -> 15m, 1h -> 1H for OKX API)
        bar = timeframe
        if timeframe.endswith('h'): bar = timeframe.upper()
        
        url = f"{self.base_url}/api/v5/market/candles?instId={instId}&bar={bar}&limit={limit}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data['code'] != '0' or not data['data']:
                return pd.DataFrame()

            # OKX returns: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
            df = pd.DataFrame(data['data'], columns=columns)
            
            # Convert types
            df['timestamp'] = pd.to_numeric(df['timestamp'])
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Sort by timestamp ascending
            df = df.sort_values('timestamp')
            
            # Calculate Indicators
            # 1. RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 2. Bollinger Bands
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['std'] = df['close'].rolling(window=20).std()
            df['upper_band'] = df['ma20'] + (2 * df['std'])
            df['lower_band'] = df['ma20'] - (2 * df['std'])

            # 3. EMA (Exponential Moving Average) - Trend Filter
            df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

            # 4. MACD (Moving Average Convergence Divergence) - Momentum
            exp12 = df['close'].ewm(span=12, adjust=False).mean()
            exp26 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp12 - exp26
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['hist'] = df['macd'] - df['signal']

            # 5. ATR (Average True Range) - Volatility
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['atr'] = true_range.rolling(window=14).mean()

            # 6. Volume MA
            df['vol_ma20'] = df['volume'].rolling(window=20).mean()
            
            return df
        except Exception as e:
            print(f"❌ 获取 K 线失败: {e}")
            return pd.DataFrame()
