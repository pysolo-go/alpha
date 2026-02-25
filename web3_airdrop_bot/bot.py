import time
import random
import sys
from web3 import Web3
from config import PRIVATE_KEY, RPC_URL, CHAIN_ID, MIN_DELAY, MAX_DELAY, TX_COUNT, WETH_ADDRESS

# WETH ABI (只包含 deposit 和 withdraw)
WETH_ABI = [
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "wad", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def setup_web3():
    """初始化 Web3 连接"""
    print(f"🔗 正在连接 RPC: {RPC_URL} ...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ 无法连接到 RPC，请检查网络或更换 RPC URL")
        sys.exit(1)
    print(f"✅ 连接成功! 当前区块高度: {w3.eth.block_number}")
    return w3

def get_account(w3):
    """从私钥加载账户"""
    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        print(f"👤 加载钱包: {account.address}")
        balance = w3.eth.get_balance(account.address)
        print(f"💰 当前余额: {w3.from_wei(balance, 'ether'):.6f} ETH")
        return account
    except Exception as e:
        print(f"❌ 私钥错误: {e}")
        sys.exit(1)

def wrap_eth(w3, account, contract, amount_eth):
    """将 ETH 包装为 WETH (Deposit)"""
    amount_wei = w3.to_wei(amount_eth, 'ether')
    print(f"🔄 [Wrap] 正在将 {amount_eth} ETH -> WETH ...")
    
    # 构建交易
    tx = contract.functions.deposit().build_transaction({
        'from': account.address,
        'value': amount_wei,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': CHAIN_ID
    })
    
    # 签名并发送
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✅ 交易已发送! Hash: {w3.to_hex(tx_hash)}")
    
    # 等待确认
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print("🎉 [Wrap] 成功!")
    else:
        print("❌ [Wrap] 失败!")

def unwrap_eth(w3, account, contract, amount_eth):
    """将 WETH 解包为 ETH (Withdraw)"""
    amount_wei = w3.to_wei(amount_eth, 'ether')
    print(f"🔄 [Unwrap] 正在将 {amount_eth} WETH -> ETH ...")
    
    # 构建交易
    tx = contract.functions.withdraw(amount_wei).build_transaction({
        'from': account.address,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(account.address),
        'chainId': CHAIN_ID
    })
    
    # 签名并发送
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✅ 交易已发送! Hash: {w3.to_hex(tx_hash)}")
    
    # 等待确认
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 1:
        print("🎉 [Unwrap] 成功!")
    else:
        print("❌ [Unwrap] 失败!")

def main():
    print("="*50)
    print("🤖 EVM 0成本空投交互机器人 v1.0")
    print("="*50)
    
    if "你的私钥" in PRIVATE_KEY:
        print("❌ 请先在 config.py 中填入私钥!")
        return

    w3 = setup_web3()
    account = get_account(w3)
    weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=WETH_ABI)
    
    print(f"\n🚀 开始执行 {TX_COUNT} 次交互任务...")
    
    for i in range(TX_COUNT):
        print(f"\n--- 第 {i+1}/{TX_COUNT} 次交互 ---")
        
        # 随机金额 (0.001 - 0.005 ETH)
        amount = round(random.uniform(0.001, 0.005), 4)
        
        # 50% 概率 Wrap, 50% 概率 Unwrap
        # 注意: 实际逻辑中应该检查 WETH 余额，这里为了简单演示随机切换
        if random.choice([True, False]):
            try:
                wrap_eth(w3, account, weth_contract, amount)
            except Exception as e:
                print(f"⚠️ Wrap 失败 (可能是余额不足): {e}")
        else:
            try:
                unwrap_eth(w3, account, weth_contract, amount)
            except Exception as e:
                print(f"⚠️ Unwrap 失败 (可能是 WETH 不足): {e}")
        
        # 随机延迟
        if i < TX_COUNT - 1:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"⏳ 等待 {delay} 秒 (模拟真人操作)...")
            time.sleep(delay)
            
    print("\n✅ 所有任务完成! 今天的空投交互已达标。")

if __name__ == "__main__":
    main()
