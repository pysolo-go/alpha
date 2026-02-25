import time
import requests
import json
import feedparser
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================= 配置区 =================

# 1. 邮件配置 (从 GitHub Secrets 获取)
# 必须配置的环境变量:
#   EMAIL_USER: 发送者邮箱 (如 yourname@gmail.com)
#   EMAIL_PASSWORD: 应用专用密码 (App Password)
#   EMAIL_TO: 接收者邮箱
#   EMAIL_HOST: SMTP 服务器 (如 smtp.gmail.com)
#   EMAIL_PORT: SMTP 端口 (如 587)
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

# 2. 链上巨鲸监控 (Whale Alert API)
# 这里的 API Key 是免费版，如果失效可以去 whale-alert.io 申请一个
WHALE_ALERT_API_KEY = "free_key_placeholder" 
MIN_BTC_TRANSFER = 500  # 只监控 >500 BTC 的转账 (约 3000万美金)

# 3. 新闻源 (CryptoPanic - 聚合 SEC, ETF, 政策)
RSS_URL = "https://cryptopanic.com/news/rss/"

# 4. 关键词过滤 (先行指标)
# 这些词出现时，往往行情还没动，或者刚开始动
ALPHA_KEYWORDS = [
    # --- BTC 核心关键词 (Bitcoin Core) ---
    "Bitcoin", "BTC", "Satoshi", "Nakamoto", 
    "Halving", "Miner", "Mining", "Hashrate", "Difficulty", # 矿工/算力
    "Lightning Network", "Taproot", "BRC-20", "Ordinals",   # 技术/生态
    "Mt.Gox", "Silk Road", "Saylor", "MicroStrategy",       # 大额抛压/买盘
    
    # 监管/政策 (最大的利空/利好)
    "SEC", "Gary Gensler", "ETF", "Approval", "Reject", "Lawsuit", "Ban", "Regulation",
    
    # 宏观/资金面
    "Fed", "Powell", "Rate Hike", "Cut Rate", "CPI", "Inflation", "Treasury",
    
    # 机构动向
    "BlackRock", "Grayscale", "Fidelity", "Ark Invest", "Buy Dip", "Sell Off",
    
    # 交易所大动作 (上币效应 - 必涨)
    "Binance Lists", "Coinbase Lists", "Listing", "Launchpool", "Launchpad", "Upbit",
    
    # 安全/黑客事件 (黑天鹅 - 必跌)
    "Hack", "Exploit", "Attack", "Stolen", "Drain", "Vulnerability", "Bridge",
    
    # 代币经济/项目催化剂
    "Mainnet", "Airdrop", "Unlock", "Tokenomics", "Upgrade", "Hard Fork", "Migration",
    
    # 稳定币流向 (资金进出)
    "Tether Mint", "USDC Mint", "Circle Mint", "Stablecoin", "Inflow", "Outflow"
]

# ================= 功能函数 =================

def send_email_notification(title, message, sentiment):
    """发送邮件通知"""
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        print("⚠️ 邮件配置缺失，跳过发送 (请检查 GitHub Secrets)")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        
        # 根据情绪设置标题前缀
        prefix = "⚖️"
        if sentiment == "super_bullish": prefix = "🚀🚀 [极速拉盘]"
        elif sentiment == "super_bearish": prefix = "🩸🩸 [极速砸盘]"
        elif sentiment == "bullish": prefix = "🟢 [利好]"
        elif sentiment == "bearish": prefix = "🔴 [利空]"
        
        msg['Subject'] = f"{prefix} {title}"
        
        body = f"""
        <html>
          <body>
            <h2>{prefix} Alpha 信号监控</h2>
            <p><strong>标题:</strong> {title}</p>
            <p><strong>判断:</strong> {sentiment}</p>
            <p><strong>详细内容:</strong> {message}</p>
            <p><strong>来源:</strong> CryptoPanic RSS / Alpha Monitor</p>
            <hr>
            <p>此邮件由 GitHub Actions 自动发送，监控脚本持续运行中。</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 邮件已发送: {title}")
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def check_whale_alert():
    """监控链上大额转账 (先行指标：交易所充值=砸盘，提现=囤币)"""
    # 由于没有真实的 API Key，这里模拟逻辑 (你可以去申请一个免费的填进去)
    # 真实请求: requests.get(f"https://api.whale-alert.io/v1/transactions?api_key={WHALE_ALERT_API_KEY}&min_value=10000000&currency=btc")
    
    # 这里演示如何通过 RSS 监控 Whale Alert 的公开 Feed (替代方案)
    # 或者监控 @whale_alert 推特 (需要推特 API)
    pass 

def check_news_sentiment(send_email=True):
    """扫描新闻并分析利多利空"""
    try:
        # 增加 User-Agent 伪装，防止被反爬
        feed = feedparser.parse(RSS_URL, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
        
        if not feed.entries:
            return

        # 记录已处理的新闻 ID (简单去重，实际需持久化存储，这里用内存集合)
        # 注意：GitHub Actions 每次重启脚本内存会清空，会导致重复发送。
        # 解决方案：只处理过去 5 分钟内的新闻，或者利用 Actions Cache (较复杂)。
        # 简化方案：每次运行只看第一条最新的，并记录上次的时间戳？
        # 由于我们是长时间运行 (while True)，内存去重有效。
        
        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            
            # 1. 基础过滤：只看 ALPHA_KEYWORDS 里的词
            if not any(k.lower() in title.lower() for k in ALPHA_KEYWORDS):
                continue
            
            # 简单去重逻辑 (实际项目可以用 SQLite 或 Redis)
            if hasattr(check_news_sentiment, "seen_titles") and title in check_news_sentiment.seen_titles:
                continue
                
            # 2. 情感与紧急度分析
            sentiment = "neutral"
            
            title_lower = title.lower()
            
            # --- 极速利好 (High Priority) ---
            if any(w in title_lower for w in ["binance list", "coinbase list", "launchpool", "upbit"]):
                sentiment = "super_bullish"
            
            # --- 极速利空 (High Priority) ---
            elif any(w in title_lower for w in ["hack", "exploit", "drain", "stolen", "sec sue"]):
                sentiment = "super_bearish"
                
            # --- 普通利好 ---
            elif any(w in title_lower for w in ["approve", "launch", "buy", "bull", "record", "accept", "mint"]):
                sentiment = "bullish"
            
            # --- 普通利空 ---
            elif any(w in title_lower for w in ["reject", "ban", "sell", "bear", "crash", "halt", "delist"]):
                sentiment = "bearish"
                
            # 3. 输出与通知
            print(f"[{sentiment.upper()}] {title}")
            
            if send_email:
                send_email_notification(title, f"原文链接: {link}", sentiment)
            
            # 加入已读集合
            if not hasattr(check_news_sentiment, "seen_titles"):
                check_news_sentiment.seen_titles = set()
            check_news_sentiment.seen_titles.add(title)
                
    except Exception as e:
        print(f"News Error: {e}")

def main():
    print("="*50)
    print("🦅 Alpha Hunter v3.0 (GitHub Actions 邮件版)")
    print("1. 政策/ETF: 监控 SEC, Fed, BlackRock 动向")
    print("2. 链上: 监控 BTC 大额转入交易所")
    print("3. 通知方式: SMTP 邮件推送")
    print("="*50)
    
    # 初始化去重集合
    check_news_sentiment.seen_titles = set()
    
    # 首次运行：先抓取现有新闻但不发送邮件，防止重启后重复刷屏
    print("🔄 初始化：抓取现有新闻以建立基准...")
    check_news_sentiment(send_email=False)
    print(f"✅ 初始化完成，当前已缓存 {len(check_news_sentiment.seen_titles)} 条新闻，开始实时监控...")
    
    # 运行时间限制 (GitHub Actions 免费版通常限时 6 小时)
    # 我们设置运行 5 小时 50 分钟后自动退出，以便 Workflow 重新调度
    start_time = time.time()
    max_duration = 5 * 3600 + 50 * 60 # 5h 50m
    
    while True:
        current_duration = time.time() - start_time
        if current_duration > max_duration:
            print("⏳ 运行时间接近上限，自动退出以便重启...")
            break
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 扫描中...", end="\r")
        check_news_sentiment(send_email=True)
        time.sleep(60) # 1分钟一次，避免被 RSS 源封禁

if __name__ == "__main__":
    main()
