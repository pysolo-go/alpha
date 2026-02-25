# OKX API Configuration
# 请填入你的 API Key (注意权限: 只读 + 交易, 不要提现!)
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
API_PASSPHRASE = "YOUR_PASSPHRASE"

# Trading Configuration
SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
    "DOGE/USDT:USDT",
    "PEPE/USDT:USDT",
    "ZRO/USDT:USDT",
    "XRP/USDT:USDT",
    "ADA/USDT:USDT",
    "SUI/USDT:USDT"
]
LEVERAGE = 5              # 杠杆倍数 (从 10x 降到 5x，稳健第一)
POSITION_SIZE_USDT = 20   # 单笔下单本金 (U)
TIMEFRAME = "1h"          # K线周期 (从 15m 改为 1h，过滤短期噪音，提高胜率)

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70       # 超买 (卖出信号)
RSI_OVERSOLD = 30         # 超卖 (买入信号)
BB_PERIOD = 20            # 布林带周期
BB_STD = 2.0              # 布林带标准差
TRAILING_STOP_PCT = 0.01  # 移动止损 (1% 回撤离场)
MAKER_MODE = True         # True=挂单模式(省钱), False=吃单模式(快)

# System
POLL_INTERVAL = 5         # 轮询间隔 (秒)
SIMULATION_MODE = True    # True=模拟盘(不真下单), False=实盘(慎用!)
INITIAL_BALANCE = 100     # 模拟盘初始本金 (U)
