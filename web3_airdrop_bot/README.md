# 0成本撸空投机器人使用指南

## 1. 准备工作 (0 成本)

### 第一步：获取钱包私钥
1. 打开 MetaMask 钱包。
2. **强烈建议创建一个新账户** (Account 2, Account 3...) 专门用于撸空投，**不要用存有大额资产的主账户**。
3. 导出该新账户的私钥 (Private Key)。

### 第二步：获取测试币 (Testnet ETH)
你需要 Sepolia ETH 作为 Gas 费 (完全免费)。去以下网站领取：
*   **Alchemy Faucet**: https://sepoliafaucet.com/ (每天可领)
*   **QuickNode Faucet**: https://faucet.quicknode.com/ethereum/sepolia
*   **PK910 Faucet**: https://sepolia-faucet.pk910.de/ (挖矿领取，给的比较多)

## 2. 配置机器人
打开 `config.py` 文件：
1. 将你的私钥填入 `PRIVATE_KEY` 字段。
2. (可选) 如果你想撸其他链 (如 Berachain, Monad)，修改 `RPC_URL` 和 `CHAIN_ID` 即可。

## 3. 运行机器人
在终端运行：
```bash
cd web3_airdrop_bot
pip install -r requirements.txt
python bot.py
```

## 4. 它是如何赚钱的？
*   这个脚本会自动在测试网上进行 Wrap/Unwrap ETH 操作。
*   每次操作都会增加你钱包的 **Tx Count (交易次数)** 和 **Active Days (活跃天数)**。
*   项目方 (如 Monad, LayerZero 等) 发空投时，通常会筛选："在测试网交互超过 10 次的用户"。
*   你坚持每天挂机跑一会儿，等空投发下来，一个号可能值几百到几千 U。
