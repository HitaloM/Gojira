# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import html

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.callback_data import StartCallback

router = Router(name="pm_menu")


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
@router.callback_query(StartCallback.filter(F.menu == "start"))
async def start_command(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("ℹ️ About"), callback_data=StartCallback(menu="about"))
    keyboard.button(text=_("🌐 Language"), callback_data=StartCallback(menu="language"))
    keyboard.button(text=_("👮‍♂️ Help"), callback_data=StartCallback(menu="help"))
    keyboard.adjust(2)

    text = _(
        "Hello, <b>{user_name}</b>. I am <b>Gojira</b>, a Telegram bot that can help \
you with informations about anime and manga, such as genres, characters, studios, \
staff. And much more!"
    ).format(user_name=html.escape(union.from_user.full_name))

    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())


@router.message(Command("help"), F.chat.type == ChatType.PRIVATE)
@router.callback_query(StartCallback.filter(F.menu == "help"))
async def help(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("👸 Anime"), callback_data=StartCallback(menu="anime"))
    keyboard.button(text=_("📖 Manga"), callback_data=StartCallback(menu="manga"))
    keyboard.adjust(2)

    if is_callback:
        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    text = _(
        "This is the menu where all my modules are concentrated, click on one of the buttons \
below to start exploring all my functions."
    )

    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())


@router.message(Command("about"))
@router.callback_query(StartCallback.filter(F.menu == "about"))
async def about(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message:
        return

    text = _(
        "Gojira is a bot developed using Python that utilizes AIOGram and \
AniList GraphQL API to provide fast, stable and comprehensive information about animes \
and mangas. The name Gojira (ゴジラ) is a reference to the Japanese name of the famous \
monster Godzilla."
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("📦 GitHub"), url="https://github.com/HitaloM/Gojira")
    keyboard.button(text=_("📚 Channel"), url="https://t.me/HitaloProjects")
    keyboard.adjust(2)

    if is_callback:
        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())
