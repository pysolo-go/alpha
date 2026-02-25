import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

# ================= 配置区 =================

# 1. 目标带单员信息
# 你可以在浏览器 F12 网络请求中找到该带单员的唯一 ID (uniqueName 或 userId)
TRADER_ID = "YOUR_TRADER_ID_HERE"  # 请替换为带单员的真实 ID
TRADER_NAME = "目标大神"  # 方便邮件里显示的名字

# 2. 邮件报警配置 (复用之前的配置)
# 请填入你的真实邮箱信息
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # 应用专用密码
EMAIL_TO = "recipient_email@qq.com"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

# 3. 监控频率 (秒)
CHECK_INTERVAL = 3  # 每3秒检查一次，太快可能被封 IP

# 4. OKX 接口地址 (注意：如果是在国内，可能需要配置代理)
# 这是移动端/网页端的公开数据接口，可能随时变动
# 示例 URL (仅供参考，实际需抓包获取最新)
API_URL = f"https://www.okx.com/priapi/v5/copy-trading/current-subpositions?uniqueName={TRADER_ID}"
# 或者
# API_URL = f"https://www.okx.com/priapi/v5/copy-trading/public-lead-trader?uniqueName={TRADER_ID}"

# ================= 功能函数 =================

def send_email_alert(subject, content):
    """发送邮件报警"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        body = f"""
        <html>
          <body>
            <h2>🚨 {subject}</h2>
            <p>{content}</p>
            <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><a href="https://www.okx.com/copy-trading">立即去跟单</a></p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 报警邮件已发送: {subject}")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def check_trader_slots():
    """检查带单员是否有空位"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    try:
        # 注意：这里模拟请求，实际开发中需要你自己抓包替换 URL 和参数
        # 假设返回 JSON 结构中有 currentCopyTraders 和 maxCopyTraders
        # resp = requests.get(API_URL, headers=headers, timeout=5)
        # data = resp.json()
        
        # --- 模拟数据 (演示用) ---
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在监控 {TRADER_NAME} 的名额...", end="\r")
        
        # 假设最大名额 500，当前 500 (满员)
        max_slots = 500
        current_slots = 500 
        
        # 模拟偶尔有人退出
        import random
        if random.random() > 0.95: # 5% 概率出现空位
            current_slots = 499
            
        # --- 核心逻辑 ---
        if current_slots < max_slots:
            available = max_slots - current_slots
            print(f"\n🎉 发现空位！剩余: {available} 个！")
            
            # 1. 发送强提醒
            send_email_alert(
                f"快抢！{TRADER_NAME} 出现 {available} 个空位！",
                f"当前跟单人数: {current_slots}/{max_slots}<br>名额稍纵即逝，请立即手动跟单！"
            )
            
            # 2. (进阶) 如果你有 API Key，这里可以直接调用 API 自动跟单
            # auto_copy_trade()
            
            return True # 发现空位后是否停止？建议继续监控直到你手动停止
            
    except Exception as e:
        print(f"\n❌ 监控出错: {e}")
        time.sleep(10) # 出错歇一会
        
    return False

def main():
    print("="*50)
    print(f"🕵️‍♀️ OKX 跟单名额监控器 v1.0")
    print(f"目标: {TRADER_NAME}")
    print(f"状态: 运行中...")
    print("="*50)
    
    while True:
        check_trader_slots()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
