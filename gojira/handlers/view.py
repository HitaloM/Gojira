# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import re

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from gojira import bot
from gojira.handlers.anime.view import anime_view
from gojira.handlers.manga.view import manga_view

router = Router(name="view")


@router.message(F.chat.type == ChatType.PRIVATE, F.via_bot)
async def view(message: Message):
    from_bot = message.via_bot
    if not from_bot:
        return

    me = await bot.get_me()
    if from_bot.id == me.id and bool(message.photo) and bool(message.caption):
        text = message.caption
        lines = text.splitlines()

        for line in lines:
            if "ID:" in line:
                matches = re.match(r"ID: (\d+) \((\w+)\)", line)
                if not matches:
                    return

                content_type: str = matches.group(2).lower()
                content_id: int = int(matches.group(1))
                if content_type == "anime":
                    await anime_view(message, anime_id=content_id)
                elif content_type == "manga":
                    await manga_view(message, manga_id=content_id)
