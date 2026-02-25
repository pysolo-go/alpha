import time
import pandas as pd
import json
import os
from config import INITIAL_BALANCE

TRADE_LOG_FILE = "trade_history.csv"
POSITION_FILE = "position_state.json"

def clear_screen():
    print("\033[H\033[J", end="")

def load_position():
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def main():
    while True:
        clear_screen()
        print(f"{'='*50}")
        print(f"💰 实时收益监控 (每 5 秒刷新)")
        print(f"{'='*50}")

        # 1. 历史交易统计
        if os.path.exists(TRADE_LOG_FILE):
            try:
                df = pd.read_csv(TRADE_LOG_FILE)
                if not df.empty:
                    # Filter for CLOSE actions to calculate realized PnL stats
                    closed_trades = df[df['Action'].str.startswith('CLOSE')]
                    total_trades = len(closed_trades)
                    
                    if total_trades > 0:
                        wins = len(closed_trades[closed_trades['PnL'] > 0])
                        win_rate = (wins / total_trades) * 100
                        total_pnl = closed_trades['PnL'].sum()
                        current_balance = df.iloc[-1]['Balance']
                    else:
                        win_rate = 0
                        total_pnl = 0
                        current_balance = INITIAL_BALANCE

                    print(f"📊 账户概览:")
                    print(f"   初始本金: {INITIAL_BALANCE} U")
                    print(f"   当前余额: {current_balance} U")
                    print(f"   总盈亏:   {total_pnl:+.2f} U ({total_pnl/INITIAL_BALANCE*100:+.2f}%)")
                    print(f"   胜率:     {win_rate:.1f}% ({wins}/{total_trades})")
                    
                    print(f"\nRecent Trades (Last 5):")
                    print(df[['Time', 'Symbol', 'Action', 'Price', 'PnL', 'Reason']].tail(5).to_string(index=False))
                else:
                    print("暂无交易记录")
            except Exception as e:
                print(f"读取日志出错: {e}")
        else:
            print(f"等待交易日志生成... ({TRADE_LOG_FILE})")

        # 2. 当前持仓监控
        pos = load_position()
        if pos:
            print(f"\n🛡️ 当前持仓:")
            print(f"   {pos['symbol']} ({pos['type'].upper()})")
            print(f"   入场价: {pos['entry_price']}")
            print(f"   持仓量: {pos['size']} U (保证金: {pos.get('amount_usdt', 'N/A')} U)")
            print(f"   最高/低: {pos.get('highest_price', pos['entry_price'])} / {pos.get('lowest_price', pos['entry_price'])}")
        else:
            print(f"\n🛡️ 当前空仓 (等待信号...)")

        print(f"\n{'='*50}")
        print(f"按 Ctrl+C 退出监控")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
