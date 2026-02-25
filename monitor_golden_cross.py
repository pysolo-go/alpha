import time
import requests
import pandas as pd
import ta
import smtplib
import os
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ================= 配置区 =================

# 1. 邮件配置
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

# 2. 监控配置
SYMBOLS = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "DOGE_USDT"]
TIMEFRAME = "1d"  # 只看日线级别 (大周期才稳)

# ================= 功能函数 =================

def send_email_alert(symbol, signal_type, details):
    """发送报警邮件"""
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        print("⚠️ 邮件配置缺失，跳过发送 (请设置 EMAIL_USER/PASSWORD/TO)")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        
        # 标题加 Emoji 醒目
        prefix = "🚀 [大牛信号]" if "金叉" in signal_type else "⚠️ [信号提醒]"
        msg['Subject'] = f"{prefix} {symbol} 出现 {signal_type}！"
        
        body = f"""
        <html>
          <body>
            <h2>{prefix} {symbol} 日线级别信号</h2>
            <p><strong>类型:</strong> {signal_type}</p>
            <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <h3>详细数据:</h3>
            <pre>{details}</pre>
            <hr>
            <p><strong>操作建议:</strong> 此信号胜率较高，建议结合盘面形态分批建仓。</p>
            <p><em>(此邮件由 Golden Cross Monitor 自动发送)</em></p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 邮件已发送: {symbol} {signal_type}")
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def get_klines(symbol, timeframe="1d", limit=200):
    """获取 K 线数据 (Gate.io)"""
    try:
        url = f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair={symbol}&interval={timeframe}&limit={limit}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Gate: [ts, vol, close, high, low, open]
            df = pd.DataFrame(data)
            # Take only first 6 columns regardless of how many returned
            df = df.iloc[:, :6]
            df.columns = ['ts', 'vol', 'c', 'h', 'l', 'o']
            for col in ['o', 'h', 'l', 'c', 'vol']:
                df[col] = pd.to_numeric(df[col])
            df['ts'] = pd.to_numeric(df['ts']) * 1000
            return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
    return None

def check_golden_cross():
    """核心逻辑: 检测 MACD 金叉 + MA 金叉 + 放量"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始扫描金叉信号...", end="\r")
    
    for symbol in SYMBOLS:
        df = get_klines(symbol, TIMEFRAME)
        if df is None or df.empty:
            continue
            
        # 1. 计算指标
        # MACD
        macd = ta.trend.MACD(close=df['c'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_hist'] = macd.macd_diff()
        
        # MA (50/200)
        df['ma50'] = ta.trend.SMAIndicator(close=df['c'], window=50).sma_indicator()
        df['ma200'] = ta.trend.SMAIndicator(close=df['c'], window=200).sma_indicator()
        
        # 成交量 MA (20)
        df['vol_ma20'] = df['vol'].rolling(window=20).mean()
        
        # 获取最近两根 K 线 (今天和昨天)
        # 注意: 如果还没收盘，这里的 iloc[-1] 是正在跳动的 K 线
        # 我们的策略是每天 08:05 运行，那时昨天的日线刚收盘，所以应该看 iloc[-2] (昨天) vs iloc[-3] (前天)?
        # 不，收盘后，iloc[-1] 是刚收完的那根。所以看 iloc[-1] 和 iloc[-2] 是对的。
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        details = ""
        
        # A. MACD 金叉 (快线上穿慢线)
        # 条件: 昨天死叉 (hist < 0) -> 今天金叉 (hist > 0)
        # 严格来说是 DEA 上穿 DIF
        if prev['macd_hist'] < 0 and curr['macd_hist'] > 0:
            signals.append("MACD 金叉")
            details += f"- MACD: 底部金叉确认 (Hist: {prev['macd_hist']:.2f} -> {curr['macd_hist']:.2f})\n"
            
        # B. 均线金叉 (MA50 上穿 MA200) - 超级牛市信号
        if prev['ma50'] < prev['ma200'] and curr['ma50'] > curr['ma200']:
            signals.append("MA50/200 黄金交叉")
            details += f"- MA Trend: 50日线上穿200日线 (牛市启动)\n"
            
        # C. 放量确认 (Volume > 1.5倍平均量)
        vol_ratio = curr['vol'] / curr['vol_ma20']
        is_high_volume = vol_ratio > 1.5
        
        if signals:
            signal_str = " + ".join(signals)
            if is_high_volume:
                signal_str += f" (🔥放量 {vol_ratio:.1f}倍)"
                details += f"- Volume: 放量 {vol_ratio:.1f}倍 (主力进场)\n"
            else:
                details += f"- Volume: 未放量 (需警惕假突破)\n"
            
            rsi_val = ta.momentum.RSIIndicator(close=df['c']).rsi().iloc[-1]
            details += f"\n当前价格: {curr['c']}\nRSI: {rsi_val:.1f}"
            
            print(f"\n🚀 发现信号: {symbol} - {signal_str}")
            send_email_alert(symbol, signal_str, details)

if __name__ == "__main__":
    print("🦅 金叉监控系统启动 (只看日线)...")
    print(f"监控币种: {SYMBOLS}")
    print("等待每日 08:05 (UTC 00:05) 触发...")
    
    # 首次运行检查一次 (测试用)
    # check_golden_cross()
    
    # 每天早上 08:05 (UTC+8 收盘后) 检查一次
    schedule.every().day.at("00:05").do(check_golden_cross) # UTC 00:05 = 北京 08:05
    
    while True:
        schedule.run_pending()
        time.sleep(60)
