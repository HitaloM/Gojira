# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.callback_data import (
    AnimeUpcomingCallback,
    MangaUpcomingCallback,
    UpcomingCallback,
)

router = Router(name="upcoming")


@router.message(Command("upcoming"), F.chat.type.in_(["group", "supergroup"]))
@router.callback_query(UpcomingCallback.filter())
async def upcoming(union: Message | CallbackQuery, callback_data: UpcomingCallback | None = None):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    user_id = callback_data.user_id if callback_data else user.id

    if callback_data and user_id != user.id:
        await union.answer(
            _("This button is not for you."),
            show_alert=True,
            cache_time=60,
        )
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=_("👸 Anime"), callback_data=AnimeUpcomingCallback(page=1, user_id=user_id)
    )
    keyboard.button(
        text=_("📖 Manga"), callback_data=MangaUpcomingCallback(page=1, user_id=user_id)
    )
    await (message.edit_text if is_callback else message.reply)(
        _("Select the type of upcoming media you want to see."),
        reply_markup=keyboard.as_markup(),
    )
