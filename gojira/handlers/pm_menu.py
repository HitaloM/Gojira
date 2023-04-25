# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Union

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.filters.chat_status import ChatIsPrivate
from gojira.utils.callback_data import StartCallback

router = Router(name="pm_menu")


@router.message(CommandStart(), ChatIsPrivate())
@router.callback_query(StartCallback.filter(F.menu == "start"))
async def start_command(union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if message is None or message.from_user is None:
        return None

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("Language"), callback_data=StartCallback(menu="language"))
    keyboard.button(text=_("About"), callback_data=StartCallback(menu="about"))
    keyboard.adjust(2)

    text = _(
        "Hello <b>{user_name}</b>, I'm Gojira! I can provide you with\
useful information about anime and manga titles"
    ).format(user_name=message.from_user.full_name)

    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())


@router.message(Command("start"), ~ChatIsPrivate())
async def group_start(message: Message):
    await message.reply(_("Hello, I'm Gojira!"))


@router.message(Command("about"))
@router.callback_query(StartCallback.filter(F.menu == "about"))
async def about(union: Union[Message, CallbackQuery]):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if message is None:
        return None

    text = _(
        "Gojira is a bot developed using Python that utilizes AIOGram and AniList GraphQL\
API to provide fast, stable and comprehensive information about animes and mangas."
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=_("GitHub"), url="https://github.com/HitaloM/Gojira"),
        InlineKeyboardButton(text=_("Channel"), url="https://t.me/HitaloProjects"),
    )
    if is_callback:
        keyboard.row(
            InlineKeyboardButton(
                text=_("Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    if is_callback:
        await message.edit_text(text, reply_markup=keyboard.as_markup())
    else:
        await message.reply(text, reply_markup=keyboard.as_markup())
