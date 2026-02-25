# 0成本撸空投机器人配置
# 警告：请务必使用【新钱包】或【空投专用钱包】，不要使用存有大额资产的主钱包！
# 私钥泄露 = 资产归零

# 1. 私钥 (Private Key) - 不需要 0x 开头，直接填
PRIVATE_KEY = "你的私钥填在这里"

# 2. 目标链配置 (这里以 Sepolia 测试网为例，完全免费)
# 你可以换成任何 EVM 兼容链 (如 Berachain Artio, Monad Testnet 等)
RPC_URL = "https://rpc.sepolia.org"
CHAIN_ID = 11155111

# 3. 交互配置
MIN_DELAY = 30  # 最小等待时间 (秒)
MAX_DELAY = 120 # 最大等待时间 (秒) - 模拟真人，防止被女巫检测
TX_COUNT = 10   # 每天运行多少次交互

# 4. WETH 合约地址 (用于 Wrap/Unwrap 刷交易量)
# Sepolia WETH 地址
WETH_ADDRESS = "0xfFf9976782d46CC05630D1f6eBAb18b2324d6B14"
