# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Union

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from babel import Locale

from gojira import i18n
from gojira.database.models import Chats, Users
from gojira.filters.user_status import IsAdmin
from gojira.utils.callback_data import LanguageCallback, StartCallback
from gojira.utils.language import get_chat_language

router = Router(name="language")


@router.message(Command("language"), IsAdmin())
@router.callback_query(StartCallback.filter(F.menu == "language"))
async def select_language(union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return None

    chat_type, lang_code = await get_chat_language(message.chat)

    lang_display_name = str(Locale.parse(lang_code).display_name).capitalize()
    if message.chat.type == ChatType.PRIVATE:
        text = _("Your language: {lang}").format(lang=lang_display_name)
    else:
        text = _("Chat language: {lang}").format(lang=lang_display_name)

    keyboard = InlineKeyboardBuilder()
    for lang in i18n.available_locales:
        lang_display_name = str(Locale.parse(lang).display_name).capitalize()
        keyboard.button(
            text=lang_display_name,
            callback_data=LanguageCallback(lang=lang, chat=chat_type),
        )

    keyboard.button(
        text=str(Locale.parse(i18n.default_locale).display_name).capitalize(),
        callback_data=LanguageCallback(lang=i18n.default_locale, chat=chat_type),
    )

    keyboard.adjust(4)
    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
        )
    )
    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())


@router.callback_query(LanguageCallback.filter(), IsAdmin())
async def language_callback(callback: CallbackQuery, callback_data: LanguageCallback):
    if not callback.message or not callback.from_user:
        return None

    if callback_data.chat == ChatType.PRIVATE:
        await Users.filter(id=callback.from_user.id).update(
            language_code=callback_data.lang
        )
    if callback_data.chat in (ChatType.GROUP, ChatType.SUPERGROUP):
        await Chats.filter(id=callback.message.chat.id).update(
            language_code=callback_data.lang
        )

    lang = Locale.parse(callback_data.lang)
    await callback.message.edit_text(
        _("Changed language to {lang}").format(lang=lang.display_name)
    )
