# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira import AniList
from gojira.utils.callback_data import (
    MangaCallback,
    MangaUpcomingCallback,
    StartCallback,
)
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="manga_upcoming")


@router.callback_query(MangaUpcomingCallback.filter())
async def manga_upcoming(callback: CallbackQuery, callback_data: MangaUpcomingCallback):
    message = callback.message
    if not message:
        return

    page = callback_data.page

    status, data = await AniList.upcoming("manga")
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
