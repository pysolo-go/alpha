#!/bin/bash

# 检查是否安装了 python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python。"
    exit 1
fi

# 安装依赖
echo "📦 正在安装依赖..."
pip3 install -r requirements.txt

# 运行机器人
echo "🚀 启动空投机器人..."
python3 bot.py
