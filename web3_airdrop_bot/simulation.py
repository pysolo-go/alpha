import time
import random
import sys

# 模拟配置
RPC_URL = "https://rpc.sepolia.org"
TX_COUNT = 5
MIN_DELAY = 1
MAX_DELAY = 3

def simulate_setup_web3():
    print(f"🔗 [模拟] 正在连接 RPC: {RPC_URL} ...")
    time.sleep(1)
    print(f"✅ [模拟] 连接成功! 当前区块高度: 5432109")

def simulate_get_account():
    print(f"👤 [模拟] 加载钱包: 0x71C...9A23 (你的新钱包)")
    time.sleep(0.5)
    print(f"💰 [模拟] 当前余额: 0.5000 ETH (测试币)")

def simulate_wrap_eth(amount):
    print(f"🔄 [模拟] 正在将 {amount:.4f} ETH -> WETH (Wrap)...")
    time.sleep(1)
    print(f"   构建交易... Gas: 0.00005 ETH")
    time.sleep(1)
    print(f"✅ [模拟] 交易已发送! Hash: 0xabc123...def456")
    time.sleep(2)
    print("🎉 [模拟] 链上确认成功! 交互次数 +1")

def simulate_unwrap_eth(amount):
    print(f"🔄 [模拟] 正在将 {amount:.4f} WETH -> ETH (Unwrap)...")
    time.sleep(1)
    print(f"   构建交易... Gas: 0.00004 ETH")
    time.sleep(1)
    print(f"✅ [模拟] 交易已发送! Hash: 0x789xyz...123456")
    time.sleep(2)
    print("🎉 [模拟] 链上确认成功! 交互次数 +1")

def main():
    print("="*50)
    print("🤖 EVM 空投机器人 [模拟运行模式]")
    print("   注意: 这是演示模式，不会消耗真金白银")
    print("="*50)
    
    simulate_setup_web3()
    simulate_get_account()
    
    print(f"\n🚀 开始执行 {TX_COUNT} 次交互演示...")
    
    for i in range(TX_COUNT):
        print(f"\n--- 第 {i+1}/{TX_COUNT} 次交互 ---")
        
        amount = random.uniform(0.001, 0.005)
        
        if random.choice([True, False]):
            simulate_wrap_eth(amount)
        else:
            simulate_unwrap_eth(amount)
        
        if i < TX_COUNT - 1:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"⏳ [模拟] 随机等待 {delay} 秒 (防女巫)...")
            time.sleep(delay)
            
    print("\n✅ 演示结束! ")
    print("👉 真实运行只需要在 config.py 填入私钥，完全一样。")

if __name__ == "__main__":
    main()
