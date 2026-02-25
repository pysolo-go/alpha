import ccxt
import time
import json
import os
import csv
from config import *

POSITION_FILE = "position_state.json"
TRADE_LOG_FILE = "trade_history.csv"

class Trader:
    def __init__(self):
        self.simulation_mode = SIMULATION_MODE
        self.position = self.load_position()  # {symbol, entry_price, size, type, highest_price, lowest_price}
        self.balance = self.load_balance()
        
        if not self.simulation_mode:
            # 实盘模式初始化 Exchange
            try:
                self.exchange = ccxt.okx({
                    'apiKey': API_KEY,
                    'secret': API_SECRET,
                    'password': API_PASSPHRASE,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'swap'}
                })
                # Check connection
                # self.exchange.load_markets() # Optional: load markets to verify connection
            except Exception as e:
                print(f"❌ 交易所连接失败: {e}")
                self.exchange = None
        else:
            self.exchange = None

    def load_balance(self):
        """从交易日志加载最新余额"""
        if os.path.exists(TRADE_LOG_FILE):
            try:
                with open(TRADE_LOG_FILE, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        last_line = lines[-1].strip().split(',')
                        return float(last_line[7]) # Balance column index
            except:
                pass
        return INITIAL_BALANCE

    def log_trade(self, symbol, action, price, amount, pnl, reason):
        """记录交易日志"""
        file_exists = os.path.exists(TRADE_LOG_FILE)
        with open(TRADE_LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Time', 'Symbol', 'Action', 'Price', 'Amount(USDT)', 'Leverage', 'PnL', 'Balance', 'Reason'])
            
            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                action,
                price,
                amount,
                LEVERAGE,
                f"{pnl:.2f}",
                f"{self.balance:.2f}",
                reason
            ])

    def load_position(self):
        """加载持仓状态"""
        if os.path.exists(POSITION_FILE):
            try:
                with open(POSITION_FILE, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_position(self):
        """保存持仓状态"""
        if self.position:
            with open(POSITION_FILE, 'w') as f:
                json.dump(self.position, f)
        else:
            if os.path.exists(POSITION_FILE):
                os.remove(POSITION_FILE)

    def place_order(self, symbol, side, price, amount_usdt):
        """下单逻辑 (支持模拟和实盘)"""
        if self.simulation_mode:
            print(f"✅ [模拟下单] {side.upper()} {symbol} @ {price}")
            print(f"   数量: {amount_usdt} U (杠杆: {LEVERAGE}x)")
            
            # Maker 模式: 假设挂单成交 (实际需要等待,这里简化直接成交)
            mode = "Maker" if MAKER_MODE else "Taker"
            print(f"   模式: {mode} (模拟成交)")

            self.position = {
                'symbol': symbol,
                'entry_price': price,
                'size': amount_usdt * LEVERAGE,
                'amount_usdt': amount_usdt, # 记录保证金
                'type': side,
                'time': time.strftime("%H:%M:%S"),
                'highest_price': price,  # For Trailing Stop (Long)
                'lowest_price': price    # For Trailing Stop (Short)
            }
            self.save_position()
            self.log_trade(symbol, f"OPEN_{side.upper()}", price, amount_usdt, 0, "Signal Entry")
            return True
        
        else:
            # 实盘下单
            if not self.exchange:
                print("❌ 交易所未连接，无法下单")
                return False

            try:
                # amount_contracts = (amount_usdt * LEVERAGE) / 100 # OKX contract size is usually 100 USD for BTC-USDT-SWAP? No.
                # WARNING: Contract size varies. For simplicity in this demo, we assume user knows.
                # Better: Use create_order with 'amount' in base currency or quote currency depending on exchange.
                # For OKX Swap, amount is in contracts. 1 contract = 0.01 BTC? Or 100 USD?
                # OKX BTC-USDT-SWAP: 1 contract = 0.01 BTC.
                # We need to calculate contracts carefully.
                
                print(f"⚠️ [实盘警告] 实盘下单功能需谨慎开启，当前仅打印日志。")
                # Uncomment to enable real trading:
                # order_type = 'limit' if MAKER_MODE else 'market'
                # order_price = price if MAKER_MODE else None
                # params = {'postOnly': True} if MAKER_MODE else {}
                
                # order = self.exchange.create_order(symbol, order_type, side, amount_contracts, order_price, params)
                # print(f"✅ 实盘下单成功: {order['id']}")
                return False # Disabled for safety
            except Exception as e:
                print(f"❌ 下单失败: {e}")
                return False

    def close_position(self, symbol, current_price, reason=""):
        """平仓逻辑"""
        if not self.position or self.position['symbol'] != symbol:
            return

        entry_price = self.position['entry_price']
        size = self.position['size']
        side = self.position['type']
        margin = self.position.get('amount_usdt', size / LEVERAGE)

        # 计算盈亏 (简化计算，不含手续费)
        pnl = 0
        if side == 'buy':
            pnl = (current_price - entry_price) * (size / entry_price)
        elif side == 'sell':
            pnl = (entry_price - current_price) * (size / entry_price)

        # 更新余额
        self.balance += pnl
        
        print(f"⚡️ [平仓] {symbol} @ {current_price} ({reason})")
        print(f"   盈亏: {pnl:.2f} U | 余额: {self.balance:.2f} U")

        self.position = None
        self.save_position()
        self.log_trade(symbol, f"CLOSE_{side.upper()}", current_price, margin, pnl, reason)

    def check_risk(self, current_price):
        """风控检查 (止损/止盈/移动止损)"""
        if not self.position:
            return

        entry_price = self.position['entry_price']
        side = self.position['type']
        highest = self.position.get('highest_price', entry_price)
        lowest = self.position.get('lowest_price', entry_price)
        
        # 1. 更新最高/最低价 (For Trailing Stop)
        if side == 'buy':
            if current_price > highest:
                highest = current_price
                self.position['highest_price'] = highest
                self.save_position() # Persist update
        elif side == 'sell':
            if current_price < lowest:
                lowest = current_price
                self.position['lowest_price'] = lowest
                self.save_position()

        # 2. 移动止损逻辑 (Trailing Stop)
        # 如果是多单: 价格从最高点回撤超过 TRAILING_STOP_PCT -> 平仓
        if side == 'buy':
            trailing_stop_price = highest * (1 - TRAILING_STOP_PCT)
            if current_price <= trailing_stop_price:
                self.close_position(self.position['symbol'], current_price, 
                                  f"触发移动止损 (最高: {highest}, 回撤: {TRAILING_STOP_PCT*100}%)")
                return

        # 如果是空单: 价格从最低点反弹超过 TRAILING_STOP_PCT -> 平仓
        elif side == 'sell':
            trailing_stop_price = lowest * (1 + TRAILING_STOP_PCT)
            if current_price >= trailing_stop_price:
                self.close_position(self.position['symbol'], current_price, 
                                  f"触发移动止损 (最低: {lowest}, 反弹: {TRAILING_STOP_PCT*100}%)")
                return

        # 3. 固定止损 (硬止损) - 作为最后的防线
        # 假设 2% 硬止损
        HARD_STOP_PCT = 0.02
        if side == 'buy':
            if current_price <= entry_price * (1 - HARD_STOP_PCT):
                self.close_position(self.position['symbol'], current_price, "触发硬止损")
        elif side == 'sell':
            if current_price >= entry_price * (1 + HARD_STOP_PCT):
                self.close_position(self.position['symbol'], current_price, "触发硬止损")
