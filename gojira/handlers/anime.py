# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
from typing import Optional, Union

import aiohttp
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.anime import ANILIST_API, ANILIST_SEARCH, ANIME_GET, TRAILER_QUERY
from gojira.utils.callback_data import GetAnimeCallback

router = Router(name="anime")


@router.message(Command("anime"))
@router.callback_query(GetAnimeCallback.filter(F.method == "get"))
async def anime(
    union: Union[Message, CallbackQuery],
    command: Optional[CommandObject] = None,
    callback_data: Optional[GetAnimeCallback] = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if message is None or user is None:
        return None

    if command and not command.args:
        await message.reply(_("You need to specify an Anime."))
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

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
                await union.answer(
                    _("This button is not for you."),
                    show_alert=True,
                    cache_time=60,
                )
                return

        is_search = callback_data.is_search
        if is_search and not is_private:
            await message.delete()

    if not bool(query):
        return

    async with aiohttp.ClientSession() as client:
        if not query.isdecimal():
            response = await client.post(
                url=ANILIST_API,
                json=dict(
                    query=ANILIST_SEARCH,
                    variables=dict(
                        search=query,
                        page=1,
                        per_page=10,
                        MediaType="ANIME",
                    ),
                ),
            )
            if response is None:
                await asyncio.sleep(0.5)
                response = await client.post(
                    url=ANILIST_API,
                    json=dict(
                        query=ANILIST_SEARCH,
                        variables=dict(
                            search=query,
                            page=1,
                            per_page=10,
                            MediaType="ANIME",
                        ),
                    ),
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            data = await response.json()
            results = data["data"]["Page"]["media"]

            if results is None or len(results) == 0:
                await message.reply(_("No results found."))
                return

            if len(results) == 1:
                anime_id = results[0]["id"]
            else:
                keyboard = InlineKeyboardBuilder()
                for result in results:
                    keyboard.row(
                        InlineKeyboardButton(
                            text=result["title"]["romaji"],
                            callback_data=GetAnimeCallback(
                                query=result["id"],
                                user_id=user.id,
                                is_search=True,
                                method="get",
                            ).pack(),
                        )
                    )
                await message.reply(
                    _("Search Results For: <b>{anime}</b>").format(anime=query),
                    reply_markup=keyboard.as_markup(),
                )
                return
        else:
            anime_id = int(query)

        response = await client.post(
            "https://graphql.anilist.co",
            json=dict(
                query=ANIME_GET,
                variables=dict(
                    id=anime_id,
                ),
            ),
        )
        data = await response.json()
        anime = data["data"]["Page"]["media"][0]

        if anime is None:
            await union.answer(
                _("No results found."),
                show_alert=True,
                cache_time=60,
            )
            return

    photo = f"https://img.anili.st/media/{anime_id}"

    studios = []
    producers = []
    for studio in anime["studios"]["nodes"]:
        if studio["isAnimationStudio"]:
            studios.append(studio["name"])
        else:
            producers.append(studio["name"])

    end_date_components = [
        component
        for component in (
            anime["endDate"].get("day"),
            anime["endDate"].get("month"),
            anime["endDate"].get("year"),
        )
        if component is not None
    ]

    start_date_components = [
        component
        for component in (
            anime["startDate"].get("day"),
            anime["startDate"].get("month"),
            anime["startDate"].get("year"),
        )
        if component is not None
    ]

    end_date = "/".join(str(component) for component in end_date_components)
    start_date = "/".join(str(component) for component in start_date_components)

    text = f"<b>{anime['title']['romaji']}</b>"
    if anime["title"]["native"]:
        text += f" (<code>{anime['title']['native']}</code>)"
    text += f"\n\n<b>ID</b>: <code>{anime['id']}</code>"
    if anime["format"]:
        text += f"\n<b>Format</b>: <code>{anime['format']}</code>"
    if not anime["format"] == "MOVIE" and anime["episodes"]:
        text += f"\n<b>Episodes</b>: <code>{anime['episodes']}</code>"
    if anime["duration"]:
        text += f"\n<b>Episode Duration</b>: <code>{anime['duration']} mins</code>"
    text += f"\n<b>Status</b>: <code>{anime['status'].capitalize()}</code>"
    if not anime["status"] == "NOT_YET_RELEASED":
        text += f"\n<b>Start Date</b>: <code>{start_date}</code>"
    if anime["status"] not in ["NOT_YET_RELEASED", "RELEASING"]:
        text += f"\n<b>End Date</b>: <code>{end_date}</code>"
    if anime["season"]:
        season = f"{anime['season'].capitalize()} {anime['seasonYear']}"
        text += f"\n<b>Season</b>: <code>{season}</code>"
    if anime["averageScore"]:
        text += f"\n<b>Average Score</b>: <code>{anime['averageScore']}</code>"
    if anime["meanScore"]:
        text += f"\n<b>Mean Score</b>: <code>{anime['meanScore']}</code>"
    if anime["studios"] and len(anime["studios"]["nodes"]) > 0:
        text += f"\n<b>Studios</b>: <code>{', '.join(studios)}</code>"
    if len(producers) > 0:
        text += f"\n<b>Producers</b>: <code>{', '.join(producers)}</code>"
    if anime["source"]:
        text += f"\n<b>Source</b>: <code>{anime['source'].capitalize()}</code>"
    if anime["genres"]:
        text += f"\n<b>Genres</b>: <code>{', '.join(anime['genres'])}</code>"

    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text=_("More Info"),
            callback_data=GetAnimeCallback(
                method="more",
                query=anime_id,
                user_id=user.id,
            ).pack(),
        )
    )

    if "relations" in anime and len(anime["relations"]["edges"]) > 0:
        relations_buttons = []
        for relation in anime["relations"]["edges"]:
            if relation["relationType"] in ["PREQUEL", "SEQUEL"]:
                button_text = (
                    _("Sequel")
                    if relation["relationType"] == "SEQUEL"
                    else _("Prequel")
                )
                relations_buttons.append(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=GetAnimeCallback(
                            query=relation["node"]["id"],
                            user_id=user.id,
                            method="get",
                        ).pack(),
                    )
                )
        if len(relations_buttons) > 0:
            if not relations_buttons[0].text == "Prequel":
                relations_buttons.reverse()
            keyboard.row(*relations_buttons)

    if bool(message.photo) and is_callback:
        await message.edit_media(
            InputMediaPhoto(type="photo", media=photo, caption=text),
            reply_markup=keyboard.as_markup(),
        )
    elif bool(message.photo) and not bool(message.via_bot):
        await message.edit_text(
            text,
            reply_markup=keyboard.as_markup(),
        )
    else:
        await message.answer_photo(
            photo,
            caption=text,
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(GetAnimeCallback.filter(F.method == "more"))
async def anime_more(callback: CallbackQuery, callback_data: GetAnimeCallback):
    message = callback.message
    user = callback.from_user
    if message is None:
        return None

    anime_id = callback_data.query
    user_id = callback_data.user_id

    if user_id != user.id:
        await callback.answer(
            _("This anime was not searched by you."),
            show_alert=True,
            cache_time=60,
        )
        return

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            "https://graphql.anilist.co",
            json=dict(
                query=TRAILER_QUERY,
                variables=dict(
                    id=(anime_id),
                    media="ANIME",
                ),
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = await response.json()
        anime = data["data"]["Page"]["media"][0]

        keyboard = InlineKeyboardBuilder()

        keyboard.add(
            InlineKeyboardButton(text=_("Description"), callback_data="*"),
            InlineKeyboardButton(text=_("Characters"), callback_data="*"),
            InlineKeyboardButton(text=_("Staff"), callback_data="*"),
            InlineKeyboardButton(text=_("Studios"), callback_data="*"),
            InlineKeyboardButton(text=_("Airing"), callback_data="*"),
        )

        if anime["trailer"]:
            trailer_site = anime["trailer"]["site"]
            trailer_id = anime["trailer"]["id"]
            trailer_url = (
                f"https://www.dailymotion.com/video/{trailer_id}"
                if trailer_site != "youtube"
                else f"https://youtu.be/{trailer_id}"
            )
            keyboard.add(
                InlineKeyboardButton(
                    text=_("Trailer"),
                    url=trailer_url,
                )
            )

        keyboard.add(InlineKeyboardButton(text=_("AniList"), url=anime["siteUrl"]))

        keyboard.adjust(2)

        keyboard.row(
            InlineKeyboardButton(
                text=_("Back"),
                callback_data=GetAnimeCallback(
                    query=anime_id,
                    user_id=user.id,
                    method="get",
                ).pack(),
            )
        )

        text = _(
            "Here you will be able to see the description, characters, staff and\
some other things, make good use of it. 🙃"
        )

        await message.edit_caption(
            caption=text,
            reply_markup=keyboard.as_markup(),
        )
