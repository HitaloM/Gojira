# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from babel import Locale

from gojira import i18n
from gojira.database import Chats, Users
from gojira.filters.users import IsAdmin
from gojira.utils.callback_data import LanguageCallback, StartCallback
from gojira.utils.language import get_chat_language

router = Router(name="language")


@router.message(Command("language"), IsAdmin())
@router.callback_query(StartCallback.filter(F.menu == "language"))
async def select_language(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return

    chat_type, lang_code = await get_chat_language(union)
    lang_display_name = str(Locale.parse(str(lang_code)).display_name).capitalize()

    text = _(
        "You can select your preferred language for the bot in this chat by clicking one of the \
buttons below.\n\n<i>These are the languages currently supported by the bot. If your language is \
not available, you can contribute by contacting @Hitalo to add it for translation.</i>\n"
    )

    if message.chat.type == ChatType.PRIVATE:
        text += _("\n<b>Your current language:</b> {lang}").format(lang=lang_display_name)
    else:
        text += _("\n<b>Group current language</b>: {lang}").format(lang=lang_display_name)

    available_locales = (*i18n.available_locales, i18n.default_locale)
    keyboard = InlineKeyboardBuilder()
    for lang in available_locales:
        lang_display_name = str(Locale.parse(lang).display_name).capitalize()
        if lang == lang_code:
            lang_display_name = f"✅ {lang_display_name}"
        keyboard.button(
            text=lang_display_name,
            callback_data=LanguageCallback(lang=lang, chat=str(chat_type)),
        )

    keyboard.adjust(2)
    keyboard.row(
        InlineKeyboardButton(
            text=_("🌎 Contribute in translations!"),
            url="https://crowdin.com/project/gojira/",
        )
    )

    if message.chat.type == ChatType.PRIVATE:
        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(LanguageCallback.filter(), IsAdmin())
async def language_callback(callback: CallbackQuery, callback_data: LanguageCallback):
    if not callback.message or not callback.from_user:
        return

    if callback_data.chat == ChatType.PRIVATE:
        await Users.set_language(user=callback.from_user, language_code=callback_data.lang)
    elif callback_data.chat in (ChatType.GROUP, ChatType.SUPERGROUP):
        await Chats.set_language(chat=callback.message.chat, language_code=callback_data.lang)

    lang = Locale.parse(callback_data.lang)
    await callback.message.edit_text(
        _("Changed language to <b>{lang}</b>").format(lang=lang.display_name)
    )
