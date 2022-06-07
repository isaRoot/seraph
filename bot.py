# from aiogram import Router
from aiogram.types import *

from misc import bot

import logging
from logging.config import fileConfig


fileConfig('logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)


# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands():
    commands = [
        BotCommand(command="/add_ru_words", description="Добавить русские слова"),
        BotCommand(command="/add_en_words", description="Добавить английские слова"),
    ]
    log.info(f'Установлен список команд BotCommandScopeChat(chat_id=4210135)')
    await bot.set_my_commands(commands, BotCommandScopeChat(chat_id=4210135))


async def send_msg2isaroot(msg):
    await bot.send_message(chat_id=4210135, text=msg)
    print()


async def send_msg2aqueisa(msg):
    await bot.send_message(chat_id=152842271, text=msg)
    print()

