# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.callback_data import (
    AnimeCategCallback,
    AnimePopuCallback,
    AnimeUpcomingCallback,
    StartCallback,
)

router = Router(name="anime_start")


@router.callback_query(StartCallback.filter(F.menu == "anime"))
async def anime_start(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("📈 Popular"), callback_data=AnimePopuCallback(page=1))
    keyboard.button(text=_("🗂️ Categories"), callback_data=AnimeCategCallback(page=1))
    keyboard.button(
        text=_("🆕 Upcoming"), callback_data=AnimeUpcomingCallback(page=1, user_id=user.id)
    )
    keyboard.button(text=_("🔍 Search"), switch_inline_query_current_chat="!a ")
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=StartCallback(menu="help").pack(),
        )
    )

    text = _("You are in the <b>anime</b> section, use the buttons below to do what you want.")
    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )
