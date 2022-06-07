import logging
from logging.config import fileConfig

from aiogram import Router, types, F
from aiogram.dispatcher.filters import Command, CommandObject

import file_db

fileConfig('logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)
router = Router()
db = file_db.Singleton()


@router.message(F.chat.type == 'private', Command(commands="start"))
async def end_start(message: types.Message):
    text = 'Добро пожаловать, поиграем? 😏'
    mc = message.chat
    uid = mc.id
    # id, user_id, main_uid, username, name, squad_id, squad_tag, squad_name
    user = db.users_get_by_uid(uid)
    if user is None:
        db.users_add_new_on_start(uid, mc.username, mc.first_name, mc.last_name)
        await message.answer(text)
    else:
        await message.answer(text)


@router.message(F.chat.type == 'private', F.chat.id == 4210135, Command(commands='add_en_words'))
async def cmd_add_en_words(message: types.Message, command: CommandObject):
    arg = command.args
    lines = arg.swapcase().lower().splitlines()
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    text = 'Успешно добавлено'
    for line in lines:
        is_good: bool = True
        li = list(line)
        if len(li) != 6:
            text = f'Слово {line} не подходит по размеру'
            break
        for l in li:
            if l not in alphabet:
                is_good = False
        if not is_good:
            text = f'Слово {line} не подходит по маске'
            break
        res = db.words_add_word_if_new('en', line)
        if res != 'success':
            text = res
            break
    await message.answer(text)


@router.message(F.chat.type == 'private', F.chat.id == 4210135, Command(commands='add_ru_words'))
async def cmd_add_ru_words(message: types.Message, command: CommandObject):
    arg = command.args
    lines = arg.swapcase().lower().splitlines()
    alphabet = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    text = 'Успешно добавлено'
    for line in lines:
        is_good: bool = True
        li = list(line)
        if len(li) != 6:
            text = f'Слово {line} не подходит по размеру'
            break
        for l in li:
            if l not in alphabet:
                is_good = False
        if not is_good:
            text = f'Слово {line} не подходит по маске'
            break
        res = db.words_add_word_if_new('ru', line)
        if res != 'success':
            text = res
            break
    await message.answer(text)
