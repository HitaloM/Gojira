# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hlink

from gojira import Jikan, bot
from gojira.utils.callback_data import ScheduleCallback

router = Router(name="anime_schedule")


@router.message(Command("schedule"))
@router.callback_query(ScheduleCallback.filter())
async def anime_schedule(
    union: Message | CallbackQuery, callback_data: ScheduleCallback | None = None
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    if is_callback and callback_data:
        user_id = callback_data.user_id
        if user_id != user.id:
            await union.answer(
                _("This button is not for you."),
                show_alert=True,
                cache_time=60,
            )
            return

    day = callback_data.day if callback_data else datetime.datetime.now(tz=datetime.UTC).weekday()
    day_map = {
        0: ["Monday", _("Monday")],
        1: ["Tuesday", _("Tuesday")],
        2: ["Wednesday", _("Wednesday")],
        3: ["Thursday", _("Thursday")],
        4: ["Friday", _("Friday")],
        5: ["Saturday", _("Saturday")],
        6: ["Sunday", _("Sunday")],
    }
    day_name = day_map.get(day, "None")
    status, data = await Jikan.schedules(day=day_name[0].lower())
    animes = data["data"]

    me = await bot.get_me()
    text = _("Below is the schedule for <b>{day}</b>:\n\n").format(day=day_name[1])
    for n, anime in enumerate(animes, start=1):
        title = anime["title"]
        malid = anime["mal_id"]
        url = f"https://t.me/{me.username}/?start=malanime_{malid}"
        text += f"<b>{n}.</b> {hlink(title=title, url=url)}\n"

    text += _(
        "\n<b>Note:</b> <i>The schedule was taken from MyAnimeList, some information about anime \
may not be available on AniList, so the bot won't be able to show information about the anime.</i>"
    )

    keyboard = InlineKeyboardBuilder()
    if day > 0:
        keyboard.button(
            text=f"⬅️ {day_map.get(day - 1, ["None", "None"])[1]}",
            callback_data=ScheduleCallback(user_id=user.id, day=day - 1),
        )
    if day < 6:
        keyboard.button(
            text=f"➡️ {day_map.get(day + 1, ["None", "None"])[1]}",
            callback_data=ScheduleCallback(user_id=user.id, day=day + 1),
        )

    await (message.edit_text if is_callback else message.reply)(
        text,
        disable_web_page_preview=True,
        reply_markup=keyboard.as_markup(),
    )
