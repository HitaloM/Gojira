# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira import AniList
from gojira.utils.callback_data import StaffCallback, StaffPopuCallback, StartCallback
from gojira.utils.keyboard import Pagination

router = Router(name="staff_popular")


@router.callback_query(StaffPopuCallback.filter())
async def staff_popular(callback: CallbackQuery, callback_data: StaffPopuCallback):
    message = callback.message
    if not message:
        return

    if isinstance(message, InaccessibleMessage):
        return

    page = callback_data.page

    _status, data = await AniList.popular("staff")
    if data["data"]:
        items = data["data"]["Page"]["staff"]
        results = [item.copy() for item in items]

        layout = Pagination(
            results,
            item_data=lambda i, _: StaffCallback(query=i["id"]).pack(),
            item_title=lambda i, _: i["name"]["full"],
            page_data=lambda pg: StaffPopuCallback(page=pg).pack(),
        )

        keyboard = layout.create(page, lines=8)

        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=_("🔙 Back"),
                callback_data=StartCallback(menu="staff").pack(),
            )
        ])

        text = _("Below are the <b>50</b> most popular staffs in descending order.")
        with suppress(TelegramAPIError):
            await message.edit_text(
                text=text,
                reply_markup=keyboard,
            )
