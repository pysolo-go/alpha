import os
import dashscope
from dashscope import Generation

# 你的 Key
dashscope.api_key = "sk-c652ad4484d24d6c8c9e0b28ba9fc287"

def test_qwen():
    print("🤖 正在呼叫通义千问 (Qwen-Turbo)...")
    try:
        messages = [
            {'role': 'system', 'content': 'You are a crypto analyst.'},
            {'role': 'user', 'content': 'Translate this to Chinese and analyze sentiment: "BlackRock files for Spot Ethereum ETF"'}
        ]
        
        response = Generation.call(
            model="qwen-turbo",
            messages=messages,
            result_format='message'
        )
        
        if response.status_code == 200:
            print("✅ API 连接成功！")
            print("回答:", response.output.choices[0].message.content)
        else:
            print(f"❌ 调用失败: {response.code} - {response.message}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_qwen()
