import asyncio
import logging

from context_var import wallet_context

logger = logging.getLogger(__name__)


async def retry_async(func, *args, retries=10, delay=5, **kwargs):
    private_key = args[0]
    wallet_context.set(private_key)
    for attempt in range(1, retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.info(f"Attempt {attempt}/{retries} failed for {func.__name__} with exception: {e}")
            if attempt == retries:
                logger.error(f"All {retries} retries failed for {func.__name__}")
                raise
            await asyncio.sleep(delay)
