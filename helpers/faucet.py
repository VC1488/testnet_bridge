import logging

import aiohttp
from web3 import AsyncWeb3, AsyncHTTPProvider

from context_var import wallet_context
from data.config import contract_address
from data.abi import abi
from helpers.proxies_random import get_random_proxy

logger = logging.getLogger(__name__)


async def faucet(private_key):
    wallet_context.set(private_key)
    proxy = get_random_proxy()
    web3 = AsyncWeb3(AsyncHTTPProvider('https://optimism-rpc.publicnode.com', request_kwargs={"proxy": proxy, "timeout": aiohttp.ClientTimeout(total=180)}))

    contract = web3.eth.contract(address=contract_address, abi=abi)

    account = web3.eth.account.from_key(private_key)
    from_address = web3.to_checksum_address(account.address)

    amount_in = int(0.000025 * 10 ** 18)
    amount_out_min = 0
    dst_chain_id = 161
    to = from_address
    refund_address = from_address
    zro_payment_address = '0x0000000000000000000000000000000000000000'
    adapter_params = b''

    priority_fee = await web3.eth.max_priority_fee
    base_fee = await web3.eth.gas_price
    max_fee_per_gas = base_fee + priority_fee

    nonce = await web3.eth.get_transaction_count(from_address)

    txn = await contract.functions.swapAndBridge(
        amount_in,
        amount_out_min,
        dst_chain_id,
        to,
        refund_address,
        zro_payment_address,
        adapter_params
    ).build_transaction({
        'from': from_address,
        'nonce': nonce,
        'gas': 1000000,
        'maxFeePerGas': int(max_fee_per_gas),
        'maxPriorityFeePerGas': int(priority_fee),
        'value': int(amount_in * 10)
    })

    signed_tx = web3.eth.account.sign_transaction(txn, private_key=private_key)

    try:
        tx_hash = await web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f'Transaction sent with hash: {web3.to_hex(tx_hash)}')
        tx_receipt = await web3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"Transaction confirmed. Status: {tx_receipt['status']}")
    except Exception as e:
        if 'insufficient funds' in str(e):
            logger.warning(f"insufficient funds for transfer")
        else:
            logger.error(f"Error occurred: {e}")
        raise
