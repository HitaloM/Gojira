# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira.utils.anime import ANILIST_API, SUGGESTIONS_QUERY
from gojira.utils.callback_data import AnimeCallback, AnimeSuggCallback, StartCallback
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="anime_suggestions")


@router.callback_query(AnimeSuggCallback.filter())
async def anime_suggestions(callback: CallbackQuery, callback_data: AnimeSuggCallback):
    message = callback.message
    if not message:
        return None

    page = callback_data.page

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            ANILIST_API,
            json=dict(
                query=SUGGESTIONS_QUERY,
                variables=dict(
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
                item_data=lambda i, pg: AnimeCallback(query=i["id"]).pack(),
                item_title=lambda i, pg: i["title"]["romaji"],
                page_data=lambda pg: AnimeSuggCallback(page=pg).pack(),
            )

            keyboard = layout.create(page, lines=8)

            keyboard.row(
                InlineKeyboardButton(
                    text=_("🔙 Back"),
                    callback_data=StartCallback(menu="anime").pack(),
                )
            )

            with suppress(TelegramAPIError):
                await message.edit_text(
                    _("Below are <b>50</b> suggestions, I hope you like some. 😅"),
                    reply_markup=keyboard.as_markup(),
                )
