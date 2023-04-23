# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.filters.chat_status import ChatIsPrivate
from gojira.handlers.language import StartCallback

router = Router(name="start")


@router.message(CommandStart(), ChatIsPrivate())
async def start_command(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("Language"), callback_data=StartCallback(menu="language"))
    keyboard.adjust(2)

    text = _(
        "Hello, I'm Gojira! I can provide you with useful information about anime and manga titles"
    )
    await message.reply(text, reply_markup=keyboard.as_markup())


@router.message(Command("start"), ~ChatIsPrivate())
async def group_start(message: Message):
    await message.reply(_("Hello, I'm Gojira!"))
