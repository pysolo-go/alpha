# OKX Quant System 使用指南

## 1. 安装依赖
确保安装了 `ccxt` 和 `pandas`:
```bash
pip install ccxt pandas
```

## 2. 配置 API (config.py)
打开 `config.py`，填入你的 OKX API Key (如果只跑模拟盘，可以不填或填 mock)。
- `SIMULATION_MODE = True` (默认): 不会真的下单，只在控制台打印。
- `SIMULATION_MODE = False`: **危险!** 会真的下单。

## 3. 运行
```bash
python3 main.py
```

## 4. 策略说明 (strategy.py)
当前策略为 **Bollinger Band + RSI Reversion**:
- **买入**: 价格跌破布林下轨 + RSI < 30 (超卖)
- **卖出**: 价格突破布林上轨 + RSI > 70 (超买)
- **止损**: 亏损 10% (价格波动 1%)
- **止盈**: 盈利 20% (价格波动 2%)

## 5. 风险提示
- 量化交易有风险，代码仅供参考。
- 实盘请务必先用小资金测试。
