# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import F, Router
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.callback_data import StartCallback, StudioPopuCallback

router = Router(name="studio_start")


@router.callback_query(StartCallback.filter(F.menu == "studio"))
async def studio_start(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message:
        return

    if isinstance(message, InaccessibleMessage):
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("📈 Popular"), callback_data=StudioPopuCallback(page=1))
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=StartCallback(menu="help").pack(),
        )
    )

    text = _("You are in the <b>studio</b> section, use the buttons below to do what you want.")
    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )
