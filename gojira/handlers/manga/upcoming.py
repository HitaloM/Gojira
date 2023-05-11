# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira.utils.callback_data import (
    MangaCallback,
    MangaUpcomingCallback,
    StartCallback,
)
from gojira.utils.graphql import ANILIST_API, UPCOMING_QUERY
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="manga_upcoming")


@router.callback_query(MangaUpcomingCallback.filter())
async def manga_upcoming(callback: CallbackQuery, callback_data: MangaUpcomingCallback):
    message = callback.message
    if not message:
        return

    page = callback_data.page

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            ANILIST_API,
            json={
                "query": UPCOMING_QUERY,
                "variables": {
                    "per_page": 50,
                    "media": "MANGA",
                },
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        data = await response.json()
        if data["data"]:
            items = data["data"]["Page"]["media"]
            suggestions = []
            for item in items:
                suggestions.append(item)

            layout = Pagination(
                suggestions,
                item_data=lambda i, pg: MangaCallback(query=int(i["id"])).pack(),
                item_title=lambda i, pg: i["title"]["romaji"],
                page_data=lambda pg: MangaUpcomingCallback(page=pg).pack(),
            )

            keyboard = layout.create(page, lines=8)

            keyboard.row(
                InlineKeyboardButton(
                    text=_("🔙 Back"),
                    callback_data=StartCallback(menu="manga").pack(),
                )
            )

            with suppress(TelegramAPIError):
                await message.edit_text(
                    _("Below are <b>50</b> items that have not yet been released."),
                    reply_markup=keyboard.as_markup(),
                )
