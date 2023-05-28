# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import time
from datetime import datetime

import humanize
from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import AniList, cache
from gojira.utils.callback_data import UserCallback, UserStatsCallback

router = Router(name="users")


@router.message(Command("user"))
@router.callback_query(UserCallback.filter())
async def user_view(
    union: Message | CallbackQuery,
    command: CommandObject | None = None,
    callback_data: UserCallback | None = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

    if command and not command.args:
        await message.reply(_("You need to specify an user. Use /user name or id"))
        return

    query = str(
        callback_data.query
        if is_callback and callback_data is not None
        else command.args
        if command and command.args
        else None
    )

    if is_callback and callback_data is not None:
        user_id = callback_data.user_id
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                return

        is_search = callback_data.is_search
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    keyboard = InlineKeyboardBuilder()
    if not query.isdecimal():
        status, data = await AniList.search("user", query)
        if not data:
            await message.reply(_("No results found."))
            return

        results = data["data"]["Page"]["users"]
        if results is None or len(results) == 0:
            await message.reply(_("No results found."))
            return

        if len(results) == 1:
            user_id = int(results[0]["id"])
        else:
            for result in results:
                keyboard.row(
                    InlineKeyboardButton(
                        text=result["name"],
                        callback_data=UserCallback(
                            query=result["id"],
                            user_id=user.id,
                            is_search=True,
                        ).pack(),
                    )
                )
            await message.reply(
                _("Search Results For: <b>{query}</b>").format(query=query),
                reply_markup=keyboard.as_markup(),
            )
            return
    else:
        user_id = int(query)

    status, data = await AniList.get("user", user_id)
    if not data:
        await message.reply(_("No results found."))
        return

    auser = data["data"]["User"]
    if auser is None:
        await union.answer(
            _("No results found."),
            show_alert=True,
            cache_time=60,
        )
        return

    text = _("<b>Username</b>: <code>{name}</code>\n").format(name=auser["name"])
    text += _("<b>ID</b>: <code>{id}</code>\n").format(id=auser["id"])
    donator = _("Yes") if auser["donatorTier"] else _("No")
    text += _("<b>Donator</b>: <code>{donator}</code>\n").format(donator=donator)
    if auser["about"]:
        if len(auser["about"]) > 200:
            auser["about"] = auser["about"][0:200] + "..."
        text += _("<b>About</b>: <code>{about}</code>\n").format(about=auser["about"])

    text += _("\n<b>Created At</b>: <code>{date}</code>\n").format(
        date=datetime.fromtimestamp(auser["createdAt"]).strftime("%d/%m/%Y")
    )
    text += _("<b>Updated At</b>: <code>{date}</code>").format(
        date=datetime.fromtimestamp(auser["updatedAt"]).strftime("%d/%m/%Y")
    )

    cached_photo = await cache.get(f"anilist_user_{auser['id']}")
    if cached_photo:
        photo = cached_photo
    else:
        photo = f"https://img.anili.st/user/{auser['id']}?a={time.time()}"

    keyboard.button(
        text=_("Anime Stats"),
        callback_data=UserStatsCallback(user_id=user_id, stat_type="anime").pack(),
    )
    keyboard.button(
        text=_("Manga Stats"),
        callback_data=UserStatsCallback(user_id=user_id, stat_type="manga").pack(),
    )
    keyboard.button(text=_("🐢 AniList"), url=auser["siteUrl"])
    keyboard.adjust(2)

    sent = await message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=keyboard.as_markup(),
    )

    if sent.photo:
        await cache.set(f"anilist_user_{auser['id']}", sent.photo[-1].file_id, expire="1h")


@router.callback_query(UserStatsCallback.filter())
async def user_stats(callback_query: CallbackQuery, callback_data: UserStatsCallback):
    user_id = callback_data.user_id
    stat_type = callback_data.stat_type

    statu, data = await AniList.get_user_stat(user_id, stat_type)
    if not data:
        await callback_query.answer(
            _("No results found."),
            show_alert=True,
            cache_time=60,
        )
        return

    text = ""

    if stat_type.lower() == "anime":
        stat = data["data"]["User"]["statistics"]["anime"]

        text = _("Total Anime Watched: {count}\n").format(count=stat["count"])
        text += _("Total Episode Watched: {episodes}\n").format(episodes=stat["episodesWatched"])
        days_watched = humanize.naturaldelta(stat["minutesWatched"] * 60, months=False)
        text += _("Total Time Spent: {time}\n").format(time=days_watched)
        text += _("Average Score: {mean_score}").format(mean_score=stat["meanScore"])

    if stat_type.lower() == "manga":
        stat = data["data"]["User"]["statistics"]["manga"]

        text = _("Total Manga Read: {count}\n").format(count=stat["count"])
        text += _("Total Chapter Read: {chapters}\n").format(chapters=stat["chaptersRead"])
        text += _("Total Volume Read: {volumes}\n").format(volumes=stat["volumesRead"])
        text += _("Average Score: {mean_score}").format(mean_score=stat["meanScore"])

    await callback_query.answer(text, show_alert=True)
