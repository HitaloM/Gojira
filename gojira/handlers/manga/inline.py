# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import random
import re
from contextlib import suppress

from aiogram import F, Router
from aiogram.enums import InlineQueryResultType
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hide_link

from gojira import AniList, bot
from gojira.utils.language import (
    i18n_anilist_format,
    i18n_anilist_source,
    i18n_anilist_status,
)

router = Router(name="manga_inline")


@router.inline_query(F.query.regexp(r"^!m (?P<query>.+)").as_("match"))
async def manga_inline(inline: InlineQuery, match: re.Match[str]):
    query = match.group("query")

    results: list[InlineQueryResult] = []

    search_results = []
    status, data = await AniList.search("manga", query)
    if not data:
        return

    search_results = data["data"]["Page"]["media"]

    if not search_results:
        return

    for result in search_results:
        status, data = await AniList.get("manga", result["id"])
        if not data:
            return

        if not data["data"]["Page"]["media"]:
            continue

        manga = data["data"]["Page"]["media"][0]

        photo: str = ""
        if banner := manga["bannerImage"]:
            photo = banner
        elif cover := manga["coverImage"]:
            if xl_image := cover["extraLarge"]:
                photo = xl_image
            elif large_image := cover["large"]:
                photo = large_image
            elif medium_image := cover["medium"]:
                photo = medium_image

        description: str = ""
        if manga["description"]:
            description = manga["description"]
            description = re.sub(re.compile(r"<.*?>"), "", description)
            description = description[0:260] + "..."

        end_date_components = [
            component
            for component in (
                manga["endDate"].get("day"),
                manga["endDate"].get("month"),
                manga["endDate"].get("year"),
            )
            if component is not None
        ]

        start_date_components = [
            component
            for component in (
                manga["startDate"].get("day"),
                manga["startDate"].get("month"),
                manga["startDate"].get("year"),
            )
            if component is not None
        ]

        end_date = "/".join(str(component) for component in end_date_components)
        start_date = "/".join(str(component) for component in start_date_components)

        text = f"<b>{manga['title']['romaji']}</b>"
        if manga["title"]["native"]:
            text += f" (<code>{manga['title']['native']}</code>)"
        text += _("\n\n<b>ID</b>: <code>{id}</code>").format(id=manga["id"]) + " (<b>MANGA</b>)"
        if await i18n_anilist_format(manga["format"]):
            text += _("\n<b>Format</b>: <code>{format}</code>").format(
                format=await i18n_anilist_format(manga["format"])
            )
        if manga["volumes"]:
            text += _("\n<b>Volumes</b>: <code>{volumes}</code>").format(volumes=manga["volumes"])
        if manga["chapters"]:
            text += _("\n<b>Chapters</b>: <code>{chapters}</code>").format(
                chapters=manga["chapters"]
            )
        if manga["status"]:
            text += _("\n<b>Status</b>: <code>{status}</code>").format(
                status=await i18n_anilist_status(manga["status"])
            )
        if manga["status"] != "NOT_YET_RELEASED":
            text += _("\n<b>Start Date</b>: <code>{date}</code>").format(date=start_date)
        if manga["status"] not in ["NOT_YET_RELEASED", "RELEASING"]:
            text += _("\n<b>End Date</b>: <code>{date}</code>").format(date=end_date)
        if manga["averageScore"]:
            text += _("\n<b>Average Score</b>: <code>{score}</code>").format(
                score=manga["averageScore"]
            )
        if manga["source"]:
            text += _("\n<b>Source</b>: <code>{source}</code>").format(
                source=await i18n_anilist_source(manga["source"])
            )
        if manga["genres"]:
            text += _("\n<b>Genres</b>: <code>{genres}</code>").format(
                genres=", ".join(manga["genres"])
            )

        text += _("\n\n<b>Short Description</b>: <i>{description}</i>").format(
            description=description
        )

        text += f"\n{hide_link(photo)}"

        keyboard = InlineKeyboardBuilder()

        me = await bot.get_me()
        bot_username = me.username
        keyboard.button(
            text=_("👓 View More"),
            url=f"https://t.me/{bot_username}/?start=manga_{manga['id']}",
        )

        results.append(
            InlineQueryResultArticle(
                type=InlineQueryResultType.ARTICLE,
                id=str(random.getrandbits(64)),
                title=manga["title"]["romaji"],
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard.as_markup(),
                description=description,
                thumbnail_url=photo,
            )
        )

    with suppress(TelegramBadRequest):
        if len(results) > 0:
            await inline.answer(results=results, is_personal=True)
