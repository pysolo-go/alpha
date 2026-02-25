from config import *

class Strategy:
    def __init__(self, symbol):
        self.symbol = symbol

    def analyze(self, df):
        """
        输入: DataFrame (包含 close, rsi, upper_band, lower_band)
        输出: (signal, reason)
        signal: 'buy', 'sell', 'hold'
        """
        if df.empty:
            return 'hold', "无数据"

        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]

        current_price = last_candle['close']
        rsi = last_candle['rsi']
        lower_band = last_candle['lower_band']
        upper_band = last_candle['upper_band']

        # 策略逻辑: MACD + EMA 趋势跟踪 + RSI 过滤 (更稳健)
        
        # 指标获取
        ema50 = last_candle['ema50']
        macd = last_candle['macd']
        signal_line = last_candle['signal']
        hist = last_candle['hist']
        prev_hist = prev_candle['hist']
        volume = last_candle['volume']
        vol_ma = last_candle['vol_ma20']

        # 1. 趋势判断 (Trend Filter)
        is_uptrend = current_price > ema50
        is_downtrend = current_price < ema50

        # 2. 动能信号 (MACD Crossover)
        # 金叉: 柱状图从负变正
        macd_golden_cross = prev_hist < 0 and hist > 0
        # 死叉: 柱状图从正变负
        macd_death_cross = prev_hist > 0 and hist < 0

        # 3. 买入逻辑 (做多)
        # 条件: 处于上升趋势 + MACD 金叉 + RSI 健康 (<70) + 成交量放大 (可选)
        if is_uptrend and macd_golden_cross and rsi < 70:
            return 'buy', f"趋势向上(Price>EMA50) + MACD金叉 + RSI健康({rsi:.1f})"

        # 4. 卖出逻辑 (做空)
        # 条件: 处于下降趋势 + MACD 死叉 + RSI 健康 (>30)
        elif is_downtrend and macd_death_cross and rsi > 30:
            return 'sell', f"趋势向下(Price<EMA50) + MACD死叉 + RSI健康({rsi:.1f})"
            
        # 5. 特殊反转逻辑 (Reversal - 可选)
        # 如果严重超卖且背离，可以尝试逆势做多 (风险较高，暂不开启)
        
        return 'hold', f"观望 (RSI:{rsi:.1f}, MACD_Hist:{hist:.4f}, EMA50:{ema50:.2f})"
