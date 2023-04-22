# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import i18n
from gojira.database.models import Chats, Users

router = Router(name="language")
sub_router = Router(name="language_callback")
router.include_router(sub_router)


class LanguageCallback(CallbackData, prefix="setlang"):
    lang: str
    chat: str


@router.message(Command("language"))
async def language(message: Message):
    keyboard = InlineKeyboardBuilder()

    if message.chat.type == ChatType.PRIVATE:
        lang = await Users.get_or_none(id=message.from_user.id)
        chat_type = "private"
    else:
        lang = await Chats.get_or_none(id=message.chat.id)
        chat_type = "group"

    if message.chat.type == ChatType.PRIVATE:
        text = f"Your language: {lang.language_code}"
    else:
        text = f"Chat language: {lang.language_code}"

    for lang in i18n.available_locales:
        keyboard.button(text=lang, callback_data=LanguageCallback(lang=lang, chat=chat_type))

    keyboard.button(text="en", callback_data=LanguageCallback(lang="en", chat=chat_type))

    keyboard.adjust(4)
    await message.reply(text, reply_markup=keyboard.as_markup())


@sub_router.callback_query(LanguageCallback.filter())
async def language_callback(callback: CallbackQuery, callback_data: LanguageCallback):
    if callback_data.chat == "private":
        await Users.filter(id=callback.from_user.id).update(language_code=callback_data.lang)
    if callback_data.chat == "group":
        await Chats.filter(id=callback.message.chat.id).update(language_code=callback_data.lang)
    else:
        return

    await callback.message.edit_text(f"Changed language to {callback_data.lang}")
