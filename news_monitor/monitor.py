import time
import feedparser
import os
import subprocess
import webbrowser
from datetime import datetime

# 配置
# 使用 CryptoPanic 的 RSS 源 (它是最快的聚合器，聚合了 CoinDesk, Cointelegraph, Twitter 等)
RSS_URL = "https://cryptopanic.com/news/rss/"

# 关键词过滤 (只提醒重要的)
KEYWORDS = [
    "Breaking", "Urgent", "SEC", "Binance", "Coinbase", 
    "ETF", "Hack", "Exploit", "Listing", "Mainnet", 
    "Airdrop", "China", "Fed", "CPI", "Interest Rate"
]

# 只要包含这些词，即使没有关键词也强制提醒 (比如 BTC 大跌)
URGENT_KEYWORDS = ["Crash", "Plunge", "Soar", "Skyrocket", "Ath", "All time high"]

# 已推送的新闻 ID (防止重复推送)
seen_ids = set()

def send_mac_notification(title, message, link):
    """发送 macOS 原生通知"""
    # 转义双引号，防止 shell 命令出错
    title = title.replace('"', '\\"')
    message = message.replace('"', '\\"')
    
    # 使用 AppleScript 发送通知
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script])
    
    # (可选) 可以在这里自动打开浏览器
    # webbrowser.open(link)

def check_news():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在扫描全网新闻...", end="\r")
    
    try:
        feed = feedparser.parse(RSS_URL)
        
        # 按时间倒序 (最新的在最前)
        for entry in feed.entries[:10]: # 只看最新的 10 条
            news_id = entry.id
            title = entry.title
            link = entry.link
            
            if news_id in seen_ids:
                continue
                
            seen_ids.add(news_id)
            
            # 检查是否包含关键词
            is_important = any(k.lower() in title.lower() for k in KEYWORDS)
            is_urgent = any(k.lower() in title.lower() for k in URGENT_KEYWORDS)
            
            if is_important or is_urgent:
                print(f"\n🚨 [突发] {title}")
                print(f"   🔗 {link}\n")
                
                # 发送 Mac 通知
                prefix = "🔥 紧急" if is_urgent else "📢 新闻"
                send_mac_notification(f"{prefix}: Crypto News", title, link)
            else:
                # 普通新闻只打印，不弹窗
                # print(f"   [普通] {title}")
                pass
                
    except Exception as e:
        print(f"\n❌ 获取新闻失败: {e}")

def main():
    print("="*50)
    print("📡 Mac Crypto News Monitor (全网监控中)")
    print("   来源: CryptoPanic (聚合 CoinDesk, Twitter, etc.)")
    print("   功能: 发现关键词 -> Mac 右上角弹窗通知")
    print("="*50)
    
    # 第一次运行先标记所有旧新闻，不推送
    print("正在初始化历史数据...")
    initial_feed = feedparser.parse(RSS_URL)
    for entry in initial_feed.entries:
        seen_ids.add(entry.id)
    print("✅ 初始化完成，开始实时监控...\n")
    
    while True:
        check_news()
        time.sleep(60) # 每 60 秒轮询一次

if __name__ == "__main__":
    main()
