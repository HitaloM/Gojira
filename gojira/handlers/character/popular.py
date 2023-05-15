# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira.utils.callback_data import CharacterCallback, CharacterPopuCallback, StartCallback
from gojira.utils.graphql import ANILIST_API, CHARACTER_POPULAR_QUERY
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="character_popular")


@router.callback_query(CharacterPopuCallback.filter())
async def character_popular(callback: CallbackQuery, callback_data: CharacterPopuCallback):
    message = callback.message
    if not message:
        return

    page = callback_data.page

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            ANILIST_API,
            json={
                "query": CHARACTER_POPULAR_QUERY,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = await response.json()

        if data["data"]:
            items = data["data"]["Page"]["characters"]
            results = []
            for item in items:
                results.append(item)

            layout = Pagination(
                results,
                item_data=lambda i, pg: CharacterCallback(query=i["id"]).pack(),
                item_title=lambda i, pg: i["name"]["full"],
                page_data=lambda pg: CharacterPopuCallback(page=pg).pack(),
            )

            keyboard = layout.create(page, lines=8)

            keyboard.row(
                InlineKeyboardButton(
                    text=_("🔙 Back"),
                    callback_data=StartCallback(menu="character").pack(),
                )
            )

            text = _(
                "Below are <b>50</b> popular in descending order, I hope you will like\
some of them. 😅"
            )
            with suppress(TelegramAPIError):
                await message.edit_text(
                    text=text,
                    reply_markup=keyboard.as_markup(),
                )
