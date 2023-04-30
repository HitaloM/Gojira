# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from gojira.utils.anime import ANILIST_API, UPCOMING_QUERY
from gojira.utils.callback_data import AnimeCallback, AnimeUpcomingCallback
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="anime_upcoming")


@router.callback_query(AnimeUpcomingCallback.filter())
async def anime_upcoming(callback: CallbackQuery, callback_data: AnimeUpcomingCallback):
    message = callback.message
    if not message:
        return None

    page = callback_data.page

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            ANILIST_API,
            json=dict(
                query=UPCOMING_QUERY,
                varianles=dict(
                    page=page,
                    media="ANIME",
                ),
            ),
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
                item_data=lambda i, pg: AnimeCallback(query=int(i["id"])).pack(),
                item_title=lambda i, pg: i["title"]["romaji"],
                page_data=lambda pg: AnimeUpcomingCallback(page=pg).pack(),
            )

            lines = layout.create(page, lines=8)

            # keyboard.row(
            #     InlineKeyboardButton(
            #         text=_("🔙 Back"),
            #         callback_data=AnimeCallback(
            #             query=anime_id,
            #             user_id=user.id,
            #         ).pack(),
            #     )
            # )

            with suppress(TelegramAPIError):
                await message.edit_text(
                    _("Below are <b>50</b> items that have not yet been released."),
                    reply_markup=lines,
                )
