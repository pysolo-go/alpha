import ccxt
import sys
from config import API_KEY, API_SECRET, API_PASSPHRASE

def test_connection():
    print(f"{'='*40}")
    print("🔑 正在验证 API Key...")
    
    if API_KEY == "YOUR_API_KEY":
        print("❌ 请先在 config.py 中填入你的 API Key！")
        return

    try:
        # 初始化交易所
        exchange = ccxt.okx({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'password': API_PASSPHRASE,
            'enableRateLimit': True,
        })
        
        # 尝试获取余额 (这是一个私有接口，只有 Key 正确才能成功)
        print("📡 连接 OKX 服务器中...")
        balance = exchange.fetch_balance()
        
        usdt_balance = balance['total'].get('USDT', 0)
        free_usdt = balance['free'].get('USDT', 0)
        
        print(f"✅ API 验证成功！")
        print(f"💰 账户总资产: {usdt_balance:.2f} USDT")
        print(f"💵 可用余额:   {free_usdt:.2f} USDT")
        
        if free_usdt < 10:
            print("⚠️ 余额不足 10 U，可能无法进行实盘交易。")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        print("💡 常见原因:")
        print("1. API Key, Secret 或 Passphrase 填错 (注意空格)")
        print("2. 权限没开 'Trade' (交易)")
        print("3. 网络问题 (需科学上网)")

    print(f"{'='*40}")

if __name__ == "__main__":
    test_connection()
