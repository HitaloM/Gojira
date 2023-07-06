# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import random
import re
from contextlib import suppress

from aiogram import F, Router
from aiogram.enums import InlineQueryResultType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineQuery, InlineQueryResult, InlineQueryResultPhoto
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import AniList, bot

router = Router(name="staff_inline")


@router.inline_query(F.query.regexp(r"^!s (?P<query>.+)").as_("match"))
async def staff_inline(inline: InlineQuery, match: re.Match[str]):
    query = match.group("query")

    results: list[InlineQueryResult] = []

    status, data = await AniList.search("staff", query)
    if not data:
        return

    search_results = data["data"]["Page"]["staff"]

    if not search_results:
        return

    for result in search_results:
        status, data = await AniList.get("staff", result["id"])
        if not data:
            return

        if not data["data"]["Page"]["staff"]:
            continue

        staff = data["data"]["Page"]["staff"][0]

        photo: str = ""
        if image := staff["image"]:
            if large_image := image["large"]:
                photo = large_image
            elif medium_image := image["medium"]:
                photo = medium_image

        description: str = ""
        if description := staff["description"]:
            description = description.replace("__", "")
            description = description.replace("**", "")
            description = description.replace("~", "")
            description = re.sub(re.compile(r"<.*?>"), "", description)
            description = description[0:260] + "..."

        text = f"**{staff['name']['full']}**"
        text += _("\n**ID**: `{id}`").format(id=staff["id"]) + " (**STAFF**)"
        if staff["language"]:
            text += _("\n**Language**: `{language}`").format(language=staff["language"])
        if staff["favourites"]:
            text += _("\n**Favourites**: `{favourites}`").format(favourites=staff["favourites"])

        text += f"\n\n{description}"

        keyboard = InlineKeyboardBuilder()

        me = await bot.get_me()
        bot_username = me.username
        keyboard.button(
            text=_("👓 View More"),
            url=f"https://t.me/{bot_username}/?start=staff_{staff['id']}",
        )

        results.append(
            InlineQueryResultPhoto(
                type=InlineQueryResultType.PHOTO,
                id=str(random.getrandbits(64)),
                photo_url=photo,
                thumbnail_url=photo,
                title=staff["name"]["full"],
                description=description,
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard.as_markup(),
            )
        )

    with suppress(TelegramBadRequest):
        if len(results) > 0:
            await inline.answer(results=results, is_personal=True)
