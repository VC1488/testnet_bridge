import asyncio
import logging

from context_var import wallet_context
from helpers.retry import retry_async
from helpers.faucet import faucet

logger = logging.getLogger(__name__)


async def process_wallet(private_key, semaphore):
    wallet_context.set(private_key)
    async with semaphore:
        try:
            await retry_async(faucet,private_key)
        except Exception as e:
            logger.error(f"Error processing wallet {private_key}: {e}")


async def processor():
    with open('data/private_keys.txt', 'r') as f:
        private_keys = [line.strip() for line in f if line.strip()]

    semaphore = asyncio.Semaphore(5)
    tasks = []

    for private_key in private_keys:
        task = asyncio.create_task(
            process_wallet(private_key, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)

    logger.info("All swaps completed.")

