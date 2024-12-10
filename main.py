import asyncio
import logging
import os
import sys

from datetime import datetime
from colorlog import ColoredFormatter
from context_var import wallet_context
from processor import processor

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def setup_logger():
    logging.getLogger('asyncio').setLevel(logging.INFO)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(log_dir, f'log_{start_time}.log')

    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-6s | %(wallet_context)s | %(message)s",
        datefmt='%m-%d %H:%M',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red'
        }
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger('asyncio').setLevel(logging.CRITICAL)

    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.wallet_context = wallet_context.get()
        return record

    logging.setLogRecordFactory(record_factory)


async def main():
    await processor()

if __name__ == '__main__':
    setup_logger()
    asyncio.run(main())