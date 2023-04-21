# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _

router = Router(name="pm menu")


@router.message(CommandStart())
async def start_command(message: Message):
    await message.reply(_("Hello, world!"))


@router.message(Command("error"))
async def crash(message: Message):
    test = 2 / 0
    print(test)
