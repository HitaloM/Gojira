# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import random
import re
from contextlib import suppress

import aiohttp
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineQuery, InlineQueryResult, InlineQueryResultPhoto
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import bot
from gojira.utils.graphql import ANILIST_API, MANGA_GET, MANGA_SEARCH

router = Router(name="manga_inline")


@router.inline_query(F.query.regexp(r"^!m (?P<query>.+)").as_("match"))
async def manga_inline(inline: InlineQuery, match: re.Match[str]):
    query = match.group("query")

    results: list[InlineQueryResult] = []

    search_results = []
    async with aiohttp.ClientSession() as client:
        if not query.isdecimal():
            response = await client.post(
                url=ANILIST_API,
                json={
                    "query": MANGA_SEARCH,
                    "variables": {
                        "per_page": 15,
                        "search": query,
                    },
                },
            )
            if not response:
                await asyncio.sleep(0.5)
                response = await client.post(
                    url=ANILIST_API,
                    json={
                        "query": MANGA_SEARCH,
                        "variables": {
                            "per_page": 10,
                            "search": query,
                        },
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            data = await response.json()
            search_results = data["data"]["Page"]["media"]

        if not search_results:
            return

        for result in search_results:
            response = await client.post(
                url=ANILIST_API,
                json={
                    "query": MANGA_GET,
                    "variables": {
                        "id": result["id"],
                    },
                },
            )
            data = await response.json()
            manga = data["data"]["Page"]["media"][0]

            if not manga:
                continue

            photo: str = ""
            if manga["bannerImage"]:
                photo = manga["bannerImage"]
            elif manga["coverImage"]:
                if manga["coverImage"]["extraLarge"]:
                    photo = manga["coverImage"]["extraLarge"]
                elif manga["coverImage"]["large"]:
                    photo = manga["coverImage"]["large"]
                elif manga["coverImage"]["medium"]:
                    photo = manga["coverImage"]["medium"]

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
            text += _("\n\n<b>ID</b>: <code>{id}</code> (<b>MANGA</b>)").format(id=manga["id"])
            if manga["format"]:
                text += _("\n<b>Format</b>: <code>{format}</code>").format(format=manga["format"])
            if manga["volumes"]:
                text += _("\n<b>Volumes</b>: <code>{volumes}</code>").format(
                    volumes=manga["volumes"]
                )
            if manga["chapters"]:
                text += _("\n<b>Chapters</b>: <code>{chapters}</code>").format(
                    chapters=manga["chapters"]
                )
            if manga["status"]:
                text += _("\n<b>Status</b>: <code>{status}</code>").format(
                    status=manga["status"].capitalize()
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
                    source=manga["source"].capitalize()
                )
            if manga["genres"]:
                text += _("\n<b>Genres</b>: <code>{genres}</code>").format(
                    genres=", ".join(manga["genres"])
                )

            text += _("\n\n<b>Short Description</b>: <i>{description}</i>").format(
                description=description
            )

            keyboard = InlineKeyboardBuilder()

            me = await bot.get_me()
            bot_username = me.username
            keyboard.button(
                text=_("👓 View More"),
                url=f"https://t.me/{bot_username}/?start=manga_{manga['id']}",
            )

            results.append(
                InlineQueryResultPhoto(
                    type="photo",
                    id=str(random.getrandbits(64)),
                    photo_url=photo,
                    thumb_url=photo,
                    title=manga["title"]["romaji"],
                    description=description,
                    caption=text,
                    reply_markup=keyboard.as_markup(),
                )
            )

    with suppress(TelegramBadRequest):
        if len(results) > 0:
            await inline.answer(
                results=results,
                is_personal=True,
                cache_time=6,
            )
