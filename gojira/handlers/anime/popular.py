# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira import AniList
from gojira.utils.callback_data import AnimeCallback, AnimePopuCallback, StartCallback
from gojira.utils.keyboard import Pagination

router = Router(name="anime_popular")


@router.callback_query(AnimePopuCallback.filter())
async def anime_popular(callback: CallbackQuery, callback_data: AnimePopuCallback):
    message = callback.message
    if not message:
        return

    page = callback_data.page

    status, data = await AniList.popular("anime")
    if data["data"]:
        items = data["data"]["Page"]["media"]
        results = [item.copy() for item in items]

        layout = Pagination(
            results,
            item_data=lambda i, _: AnimeCallback(query=i["id"]).pack(),
            item_title=lambda i, _: i["title"]["romaji"],
            page_data=lambda pg: AnimePopuCallback(page=pg).pack(),
        )

        keyboard = layout.create(page, lines=8)

        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"),
                callback_data=StartCallback(menu="anime").pack(),
            )
        )

        text = _("Below are the <b>50</b> most popular animes in descending order.")
        with suppress(TelegramAPIError):
            await message.edit_text(
                text=text,
                reply_markup=keyboard.as_markup(),
            )
