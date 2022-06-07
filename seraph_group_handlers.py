import logging
from logging.config import fileConfig

from aiogram import types, Router

import file_db
from misc import bot

router = Router()
db = file_db.Singleton()

fileConfig('logging.ini', disable_existing_loggers=False)
log = logging.getLogger(__name__)


@router.my_chat_member()
async def end_new_group(my_chat_member: types.ChatMemberUpdated):
    if my_chat_member.chat.type in ('group', 'supergroup'):
        if my_chat_member.old_chat_member.status in ('kicked', 'left'):
            if my_chat_member.new_chat_member.status in ('member', 'administrator'):
                if my_chat_member.new_chat_member.user.id == bot.id:
                    group_ch = db.group_chat_get_by_id(my_chat_member.chat.id)
                    if group_ch is None:
                        db.group_chat_add_new(my_chat_member.chat.id, my_chat_member.chat.linked_chat_id,
                                              my_chat_member.chat.title, my_chat_member.chat.description,
                                              # .full_name, TODO: допилинг этого хреньки
                                              my_chat_member.chat.description, my_chat_member.chat.type)
                        await bot.send_message(my_chat_member.chat.id,
                                               f'Больше чатов богу чатов\n'
                                               f'особенно с id: {my_chat_member.chat.id}')
                    else:
                        db.group_chat_update(my_chat_member.chat.id, my_chat_member.chat.linked_chat_id,
                                             my_chat_member.chat.title, my_chat_member.chat.description,
                                             # .full_name, TODO: допилинг этого хреньки
                                             my_chat_member.chat.description, my_chat_member.chat.type, 1)
                        await bot.send_message(my_chat_member.chat.id,
                                               f'ну что? одумались?\n'
                                               f'id: <code>{my_chat_member.chat.id}<code>')
        elif my_chat_member.old_chat_member.status in ('member', 'administrator'):
            if my_chat_member.new_chat_member.status in (
                    'kicked', 'left'):  # TODO: допилинг этой хреньки, или валидашка
                if my_chat_member.new_chat_member.user.id == bot.id:
                    group_ch = db.group_chat_get_by_id(my_chat_member.chat.id)
                    if group_ch is not None:
                        db.group_chat_update(my_chat_member.chat.id, my_chat_member.chat.linked_chat_id,
                                             my_chat_member.chat.title, my_chat_member.chat.title,
                                             # my_chat_member.chat.full_name, TODO: допилинг этого хреньки
                                             my_chat_member.chat.description, my_chat_member.chat.type, 0)


@router.message(content_types="migrate_to_chat_id")
async def group_upgrade_to(message: types.Message):
    new_group_chat = db.group_chat_get_by_id(message.migrate_to_chat_id)
    old_group_chat = db.group_chat_get_by_id(message.chat.id)
    if new_group_chat is None:
        db.group_chat_update_on_upgrade_group(message.chat.id, message.migrate_to_chat_id)
    else:
        db.group_chat_delete(message.chat.id)
    await bot.send_message(message.migrate_to_chat_id, f'Группа апнута до супергруппы\n'
                                                       f'Old ID: <code>{message.chat.id}</code>\n'
                                                       f'New ID: <code>{message.migrate_to_chat_id}</code>')
