# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import re

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from gojira import bot
from gojira.handlers.anime.view import anime_view
from gojira.handlers.character.view import character_view
from gojira.handlers.manga.view import manga_view
from gojira.handlers.staff.view import staff_view

router = Router(name="view")


@router.message(F.chat.type == ChatType.PRIVATE, F.via_bot)
async def view(message: Message):
    if not message.via_bot:
        return

    me = await bot.get_me()
    if message.via_bot.id == me.id and message.photo or message.text:
        for line in (
            message.caption.splitlines()
            if message.caption
            else message.text.splitlines()
            if message.text
            else []
        ):
            if "ID:" in line:
                matches = re.match(r"ID: (\d+) \((\w+)\)", line)
                if matches:
                    content_type, content_id = (
                        matches.group(2).lower(),
                        int(matches.group(1)),
                    )

                    if content_type == "anime":
                        await anime_view(message, anime_id=content_id)
                    elif content_type == "manga":
                        await manga_view(message, manga_id=content_id)
                    elif content_type == "character":
                        await character_view(message, character_id=content_id)
                    elif content_type == "staff":
                        await staff_view(message, staff_id=content_id)
