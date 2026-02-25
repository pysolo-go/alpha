import time
import sys
from concurrent.futures import ThreadPoolExecutor
from config import *
from market import MarketData
from strategy import Strategy
from trader import Trader

def process_symbol(symbol, market, strategies, trader):
    """处理单个币种的完整流程"""
    try:
        # A. 获取数据
        ticker = market.get_ticker(symbol)
        if not ticker:
             # print(f"⚠️ [{symbol}] 获取行情失败") # 减少日志噪音
             return
        current_price = ticker['last']
        
        df = market.fetch_ohlcv(symbol, TIMEFRAME)
        if df.empty:
            # print(f"⚠️ [{symbol}] 获取K线失败")
            return
            
        # B. 策略分析
        strategy = strategies[symbol]
        signal, reason = strategy.analyze(df)
        
        # C. 执行交易
        if signal == 'buy':
            print(f"\n🔥 [{symbol}] [买入信号] {reason}")
            # 简单的单持仓限制：整个系统同一时间只持有一个币种
            # 如果需要每个币种独立持仓，这里需要修改逻辑
            if not trader.position: 
                trader.place_order(symbol, 'buy', current_price, POSITION_SIZE_USDT)
        
        elif signal == 'sell':
            print(f"\n🔥 [{symbol}] [卖出信号] {reason}")
            if not trader.position:
                trader.place_order(symbol, 'sell', current_price, POSITION_SIZE_USDT)
        
        # D. 风控检查 (如果持仓且是当前币种)
        if trader.position and trader.position['symbol'] == symbol:
            print(f"   🛡️ [{symbol}] 持仓监控中... (当前价: {current_price})")
            trader.check_risk(current_price)
            
    except Exception as e:
        print(f"❌ [{symbol}] 处理异常: {e}")

def main():
    print(f"{'='*50}")
    print(f"🤖 OKX 量化交易系统 v1.1 (多线程急速版)")
    print(f"🎯 监控交易对: {SYMBOLS}")
    print(f"⚡️ 杠杆: {LEVERAGE}x | 本金: {POSITION_SIZE_USDT} U")
    print(f"🛠️ 模式: {'模拟盘 (Simulation)' if SIMULATION_MODE else '实盘 (Real Trading)'}")
    print(f"{'='*50}")

    # 1. 初始化模块
    try:
        market = MarketData()
        trader = Trader() 
        strategies = {symbol: Strategy(symbol) for symbol in SYMBOLS} 
        print("✅ 系统初始化完成")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 2. 主循环
    print("\n🚀 开始运行多线程极速监控 (按 Ctrl+C 停止)...")
    
    # 创建线程池 (最大线程数 = 币种数量，保证完全并行)
    executor = ThreadPoolExecutor(max_workers=len(SYMBOLS))
    
    try:
        while True:
            start_time = time.time()
            
            # 并发提交任务
            futures = []
            for symbol in SYMBOLS:
                futures.append(executor.submit(process_symbol, symbol, market, strategies, trader))
            
            # 等待本轮所有任务完成
            for future in futures:
                future.result()
                
            elapsed = time.time() - start_time
            print(f"\r⚡️ 全网扫描完成 (耗时 {elapsed:.2f}s) | 等待 {POLL_INTERVAL} 秒...", end="")
            
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n👋 系统已停止。")
        executor.shutdown(wait=False)

if __name__ == "__main__":
    main()
