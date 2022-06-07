import asyncio
import logging
from logging.config import fileConfig

from aiogram import Dispatcher

import seraph_agent_handler
import seraph_group_handlers
import seraph_handler
from misc import bot

fileConfig('logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)


# Запуск процесса поллинга новых апдейтов
async def main():
    log.info("Запуск приложения.")
    dp = Dispatcher()
    dp.include_router(seraph_handler.router)
    dp.include_router(seraph_agent_handler.router)
    dp.include_router(seraph_group_handlers.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



