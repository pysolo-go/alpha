# 🦞 OpenClaw (龙虾) 部署指南

## 1. 选哪家云服务器？(Critical Choice)

**强烈建议：不要用腾讯云/阿里云国内版！**
*   **原因 1 (网络)**: OpenClaw 需要调用 Claude/GPT 的 API，也需要访问 CryptoPanic/Twitter 等数据源。**国内服务器访问这些全部被墙，连不上！**
*   **原因 2 (风控)**: 国内云厂商对“加密货币/挖矿/自动脚本”监控极严，容易被封机。

### ✅ 推荐方案 (必须是海外节点)

#### A. 性价比之王 (新手推荐)
*   **厂商**: **Vultr** 或 **DigitalOcean**
*   **节点**: 选择 **新加坡 (Singapore)** 或 **日本 (Tokyo)** (延迟低)。
*   **配置**: 
    *   **CPU**: 1 vCPU (2 vCPU 更好)
    *   **内存**: 2GB (如果跑浏览器任务建议 4GB)
    *   **价格**: 约 $10 - $24 / 月 (按小时计费，随时可删)
*   **优点**: 注册简单，支持支付宝/微信支付 (Vultr)，网络通畅无阻。

#### B. 极致便宜 (进阶)
*   **厂商**: **Hetzner** (德国老牌)
*   **配置**: 2 vCPU + 4GB 内存
*   **价格**: 约 €5 / 月 (超级便宜)
*   **缺点**: 注册审核严格，可能需要护照验证，节点在欧洲延迟稍高（但机器跑脚本无所谓）。

#### C. 如果你非要用腾讯/阿里
*   **必须买**: **腾讯云/阿里云的【海外版】 (如香港/新加坡节点)**。
*   **千万别买**: 北京/上海/杭州节点。
*   **注意**: 价格通常比 Vultr 贵很多，且带宽小。

---

## 2. 部署步骤 (保姆级)

假设你买了一台 **Ubuntu 22.04** 的海外服务器。

### 第一步：连接服务器
在你的电脑终端 (Terminal) 输入：
```bash
ssh root@你的服务器IP
# 然后输入密码
```

### 第二步：安装环境 (Docker 方式最简单)
OpenClaw 官方推荐用 Docker 部署，省去配环境的麻烦。

1.  **安装 Docker**:
    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    ```

2.  **拉取 OpenClaw 镜像**:
    ```bash
    # 注意：这里以 OpenClaw 的社区镜像为例，具体看官方最新文档
    docker pull ghcr.io/openclaw/openclaw:latest
    ```

### 第三步：配置大脑 (API Key)
你需要告诉它用谁的大脑（推荐 Claude 3.5 Sonnet，写代码/分析能力最强）。

1.  创建配置文件 `.env`:
    ```bash
    nano .env
    ```
2.  粘贴以下内容 (替换成你的 Key):
    ```env
    # 大脑配置
    LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=sk-ant-api03-xxxxxx  # 去 console.anthropic.com 申请
    
    # 允许执行的权限 (小心!)
    ALLOW_SHELL=true
    ALLOW_FILE_WRITE=true
    ```
3.  按 `Ctrl+O` 保存，`Ctrl+X` 退出。

### 第四步：启动龙虾 🦞
```bash
docker run -d \
  --name my-lobster \
  --env-file .env \
  -v $(pwd)/workspace:/app/workspace \
  ghcr.io/openclaw/openclaw:latest
```

### 第五步：怎么跟它说话？
OpenClaw 通常会提供一个 Web 界面或者通过 Telegram Bot 交互。
*   **推荐**: 配置 Telegram Bot Token，这样你就在微信/TG 上直接给它发号施令：“帮我监控 BTC 价格，跌破 62000 叫我。”

---

## 3. 进阶玩法：让它跑我们的脚本
还记得之前写的 `alpha_monitor.py` 吗？
你可以把它通过 `docker cp` 命令扔进容器里，然后让 OpenClaw 定时运行它。

```bash
# 把脚本复制进去
docker cp alpha_monitor.py my-lobster:/app/workspace/

# 让它运行
docker exec -it my-lobster python workspace/alpha_monitor.py
```

## ⚠️ 安全警告
*   **不要给 Root 权限**: 尽量创建一个普通用户跑 Docker。
*   **API Key 保护**: `.env` 文件里有你的钱包私钥或 API Key，千万别发给别人！
*   **限制消费**: 在 OpenAI/Anthropic 后台设置 **额度上限 (Usage Limit)**，防止脚本死循环把你的卡刷爆。
