import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ================= 配置区 =================

# 1. 数据来源：
# 由于 OKX API 限制非跟单用户查看实时持仓，我们只能分析【历史战绩】(History)
# 请在浏览器 F12 Network 中抓取该带单员的 "history-positions" 接口数据
# 将 Response 保存为 'trader_history.json' 文件放在同目录下
DATA_FILE = "trader_history.json"

# ================= 分析逻辑 =================

def load_data(file_path):
    """加载 JSON 数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 根据 OKX 实际返回结构调整
        # 通常在 data['data'] 或 data['data'][0]['details'] 里
        if 'data' in data:
            records = data['data']
        else:
            records = data
            
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return None

def analyze_performance(df):
    """核心指标分析"""
    if df is None or df.empty:
        print("⚠️ 数据为空，无法分析")
        return

    # 1. 数据清洗与转换
    # 假设字段名如下 (需根据实际 JSON 调整)
    # openTime: 开仓时间 (ms)
    # closeTime: 平仓时间 (ms)
    # symbol: 币种 (BTC-USDT-SWAP)
    # side: 方向 (long/short)
    # lever: 杠杆倍数
    # pnl: 收益额 (USDT)
    # pnlRatio: 收益率 (%)
    
    # 转换时间戳
    if 'closeTime' in df.columns:
        df['close_time'] = pd.to_datetime(df['closeTime'], unit='ms')
    
    # 转换数值类型
    numeric_cols = ['pnl', 'pnlRatio', 'lever']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. 基础统计
    total_trades = len(df)
    win_trades = len(df[df['pnl'] > 0])
    loss_trades = len(df[df['pnl'] <= 0])
    win_rate = (win_trades / total_trades) * 100
    
    total_profit = df[df['pnl'] > 0]['pnl'].sum()
    total_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
    pnl_ratio = total_profit / total_loss if total_loss != 0 else float('inf')
    
    avg_leverage = df['lever'].mean() if 'lever' in df.columns else 0
    
    print("="*50)
    print("📊 交易员战绩深度透视")
    print("="*50)
    print(f"总交易笔数: {total_trades}")
    print(f"胜率 (Win Rate): {win_rate:.2f}%  ({'🔥 牛逼' if win_rate > 60 else '😐 一般'})")
    print(f"盈亏比 (P/L Ratio): {pnl_ratio:.2f}  (每亏1U能赚多少U)")
    print(f"平均杠杆: {avg_leverage:.1f}x")
    print(f"最大单笔盈利: {df['pnl'].max():.2f} U")
    print(f"最大单笔亏损: {df['pnl'].min():.2f} U")
    
    # 3. 风格画像
    print("-" * 30)
    print("🧘‍♂️ 交易风格画像:")
    
    # 持仓时间分析
    if 'openTime' in df.columns and 'closeTime' in df.columns:
        df['duration_min'] = (df['closeTime'] - df['openTime']) / 1000 / 60
        avg_duration = df['duration_min'].mean()
        
        style = "未知"
        if avg_duration < 60: style = "超短线/高频 (Scalping)"
        elif avg_duration < 1440: style = "日内波段 (Day Trading)"
        else: style = "中长线趋势 (Swing Trading)"
        
        print(f"• 持仓习惯: {style} (平均 {avg_duration:.1f} 分钟)")
    
    # 偏好币种
    if 'symbol' in df.columns:
        fav_coin = df['symbol'].mode()[0]
        print(f"• 最爱做的币: {fav_coin}")
        
    # 4. 风险提示
    print("-" * 30)
    print("⚠️ 潜在风险点:")
    
    # 检查是否扛单 (亏损单持仓时间显著长于盈利单)
    if 'duration_min' in df.columns:
        avg_win_duration = df[df['pnl'] > 0]['duration_min'].mean()
        avg_loss_duration = df[df['pnl'] < 0]['duration_min'].mean()
        
        if avg_loss_duration > avg_win_duration * 2:
            print(f"❗ 严重扛单嫌疑！(亏损单平均拿 {avg_loss_duration:.1f}m vs 盈利单 {avg_win_duration:.1f}m)")
            print("  -> 说明他不止损，喜欢死扛回来。这种人一旦遇到单边行情会爆仓。")
        else:
            print("✅ 止损坚决 (亏损单处理得很快)")

    # 检查是否有马丁策略 (连续亏损后加仓)
    # (此处仅为简单逻辑，需结合开仓时间排序分析)
    
    # 5. 绘图 (可选)
    # plot_pnl_curve(df)

def plot_pnl_curve(df):
    """绘制资金曲线"""
    try:
        df = df.sort_values('close_time')
        df['cumulative_pnl'] = df['pnl'].cumsum()
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['close_time'], df['cumulative_pnl'], label='Cumulative PnL')
        plt.title('Trader PnL Curve')
        plt.xlabel('Date')
        plt.ylabel('USDT')
        plt.grid(True)
        plt.legend()
        plt.savefig('trader_pnl_curve.png')
        print("📈 资金曲线图已保存为 'trader_pnl_curve.png'")
    except Exception as e:
        print(f"绘图失败: {e}")

if __name__ == "__main__":
    # 检查文件是否存在
    import os
    if not os.path.exists(DATA_FILE):
        print(f"❌ 未找到数据文件: {DATA_FILE}")
        print("请先去 OKX 网页版抓包 'history-positions' 接口数据，保存为该文件名。")
        print("或者手动创建一个包含测试数据的 JSON 文件。")
    else:
        df = load_data(DATA_FILE)
        analyze_performance(df)
