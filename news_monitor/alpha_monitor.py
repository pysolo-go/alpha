import time
import requests
import json
import feedparser
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dashscope
from dashscope import Generation

# ================= 配置区 =================

# 1. 邮件配置
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))

# 2. 通义千问 API 配置
# 从 GitHub Secrets 获取 DASHSCOPE_API_KEY
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

# 3. 新闻源
RSS_URL = "https://cryptopanic.com/news/rss/"

# 4. 关键词过滤
ALPHA_KEYWORDS = [
    "Bitcoin", "BTC", "ETH", "Ethereum", "SEC", "ETF", "Binance", "BlackRock", 
    "Hack", "Exploit", "Fed", "CPI", "Inflation", "Rate", "Approval"
]

# ================= AI 分析函数 =================

def analyze_with_ai(title, link):
    """使用通义千问分析新闻"""
    if not dashscope.api_key:
        return None, "neutral", "AI Key 未配置"
        
    try:
        prompt = f"""
        你是一个专业的加密货币分析师。请分析以下新闻标题，并给出简短的中文解读。
        
        新闻标题: "{title}"
        
        请按以下 JSON 格式返回 (不要包含 markdown 代码块):
        {{
            "sentiment": "利好" / "利空" / "中性",
            "summary": "一句话中文总结发生了什么",
            "analysis": "简短分析对币价的影响 (50字以内)",
            "action": "建议操作 (如: 关注BTC支撑位 / 逢高做空 / 观望)"
        }}
        """
        
        response = Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            # 尝试解析 JSON，如果 AI 返回了 markdown code block，清理一下
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        else:
            print(f"AI Error: {response.code}")
            return None
            
    except Exception as e:
        print(f"AI Exception: {e}")
        return None

# ================= 邮件发送 =================

def send_email_notification(title, ai_result, link):
    """发送增强版邮件"""
    if not EMAIL_USER or not EMAIL_PASSWORD or not EMAIL_TO:
        print("⚠️ 邮件配置缺失")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        
        sentiment = ai_result.get('sentiment', '中性')
        prefix = "⚖️"
        if "利好" in sentiment: prefix = "🚀 [利好]"
        elif "利空" in sentiment: prefix = "🩸 [利空]"
        
        msg['Subject'] = f"{prefix} {ai_result.get('summary', title)}"
        
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #333;">{prefix} Alpha 智能监控</h2>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p><strong>🤖 AI 判读:</strong> <span style="font-size: 18px; font-weight: bold; color: {'red' if '利空' in sentiment else 'green'}">{sentiment}</span></p>
                <p><strong>📝 中文总结:</strong> {ai_result.get('summary')}</p>
                <p><strong>📊 深度分析:</strong> {ai_result.get('analysis')}</p>
                <p><strong>💡 操作建议:</strong> {ai_result.get('action')}</p>
            </div>
            
            <p><strong>原文标题:</strong> {title}</p>
            <p><a href="{link}">点击查看原文</a></p>
            
            <hr>
            <p style="font-size: 12px; color: #888;">Powered by Qwen-Turbo & GitHub Actions</p>
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

# ================= 主逻辑 =================

def check_news_sentiment():
    """扫描新闻并分析"""
    try:
        feed = feedparser.parse(RSS_URL, agent="Mozilla/5.0")
        if not feed.entries: return

        # 简单去重 (实际运行中需更完善的去重)
        if not hasattr(check_news_sentiment, "seen_titles"):
            check_news_sentiment.seen_titles = set()
            
        for entry in feed.entries[:3]: # 每次只处理最新的 3 条
            title = entry.title
            link = entry.link
            
            if title in check_news_sentiment.seen_titles: continue
            
            # 关键词过滤
            if not any(k.lower() in title.lower() for k in ALPHA_KEYWORDS):
                continue
                
            print(f"🔍 发现新闻: {title}")
            
            # 调用 AI 分析
            ai_result = analyze_with_ai(title, link)
            
            if ai_result:
                send_email_notification(title, ai_result, link)
            else:
                # AI 失败时的兜底
                pass 
                
            check_news_sentiment.seen_titles.add(title)
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("🦅 Alpha Hunter AI 版启动...")
    check_news_sentiment.seen_titles = set()
    
    # 运行一次 (GitHub Actions 调度)
    check_news_sentiment()

if __name__ == "__main__":
    main()
