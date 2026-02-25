import subprocess
import time

def send_mac_notification(title, message, sound="Glass"):
    """发送 Mac 原生通知"""
    print(f"🔊 正在播放: {sound} - {title}")
    # 转义双引号，防止 shell 命令报错
    title = title.replace('"', '\\"')
    message = message.replace('"', '\\"')
    script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
    subprocess.run(["osascript", "-e", script])

def main():
    print("🎧 开始模拟 Alpha 信号音效...")
    print("请确保你的电脑音量已开启。\n")

    # 1. 极速利好 (Super Bullish) - Ping
    time.sleep(1)
    send_mac_notification("🚀🚀 [极速拉盘] Binance Lists PIPPIN", "🟢 交易所上币/重大利好", "Ping")
    print("   -> 对应场景：币安/Coinbase 上币，必须马上冲！\n")
    
    # 2. 极速利空 (Super Bearish) - Basso
    time.sleep(3)
    send_mac_notification("🩸🩸 [极速砸盘] Curve Finance Hacked", "🔴 黑客攻击/SEC起诉", "Basso")
    print("   -> 对应场景：黑客攻击、SEC 起诉，必须马上跑！\n")

    # 3. 普通消息 (Normal) - Glass
    time.sleep(3)
    send_mac_notification("⚖️ [关注] Tether Mints 1B USDT", "✅ 潜在利好/资金流入", "Glass")
    print("   -> 对应场景：增发、解锁、一般性利好/利空。\n")

    print("✅ 模拟结束。")

if __name__ == "__main__":
    main()
