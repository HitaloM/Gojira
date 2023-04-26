# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
from typing import Optional, Union

import aiohttp
from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.utils.anime import ANILIST_API, ANILIST_SEARCH, ANIME_GET
from gojira.utils.callback_data import GetAnimeCallback

router = Router(name="anime")


@router.message(Command("anime"))
@router.callback_query(GetAnimeCallback.filter())
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
        else command.args.split(" ")[0]
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
                            ).pack(),
                        )
                    )
                await message.reply(
                    _("Search results for: {anime}").format(anime=query),
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

    text = f"<b>{anime['title']['romaji']}</b>"
    if anime["title"]["native"]:
        text += f" (<code>{anime['title']['native']}</code>)"
    text += f"\n\n<b>ID</b>: <code>{anime['id']}</code>"
    if "format" in anime:
        text += f"\n<b>Format</b>: <code>{anime['format']}</code>"
    if not anime["format"] == "MOVIE" and "episodes" in anime:
        text += f"\n<b>Episodes</b>: <code>{anime['episodes']}</code>"
    if "duration" in anime:
        text += f"\n<b>Episode Duration</b>: <code>{anime['duration']} mins</code>"
    text += f"\n<b>Status</b>: <code>{anime['status'].capitalize()}</code>"
    if not anime["status"] == "NOT_YET_RELEASED":
        text += f"\n<b>Start Date</b>: <code>{anime['startDate']['day'] if anime['startDate']['day'] else 0}/{anime['startDate']['month'] if anime['startDate']['month'] else 0}/{anime['startDate']['year'] if anime['startDate']['year'] else 0}</code>"
    if anime["status"] not in ["NOT_YET_RELEASED", "RELEASING"]:
        text += f"\n<b>End Date</b>: <code>{anime['endDate']['day'] if anime['endDate']['day'] else 0}/{anime['endDate']['month'] if anime['endDate']['month'] else 0}/{anime['endDate']['year'] if anime['endDate']['year'] else 0}</code>"
    if "season" in anime:
        text += f"\n<b>Season</b>: <code>{anime['season'].capitalize()} {anime['seasonYear']}</code>"
    if "averageScore" in anime:
        text += f"\n<b>Average Score</b>: <code>{anime['averageScore']}</code>"
    if "meanScore" in anime:
        text += f"\n<b>Mean Score</b>: <code>{anime['meanScore']}</code>"
    if "studios" in anime and len(anime["studios"]["nodes"]) > 0:
        text += f"\n<b>Studios</b>: <code>{', '.join(studios)}</code>"
    if len(producers) > 0:
        text += f"\n<b>Producers</b>: <code>{', '.join(producers)}</code>"
    if "source" in anime:
        text += f"\n<b>Source</b>: <code>{anime['source'].capitalize()}</code>"
    if "genres" in anime:
        text += f"\n<b>Genres</b>: <code>{', '.join(anime['genres'])}</code>"

    keyboard = InlineKeyboardBuilder()

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
                            is_search=False,
                        ).pack(),
                    )
                )
        if len(relations_buttons) > 0:
            if not relations_buttons[0].text == "Prequel":
                relations_buttons.reverse()
            keyboard.add(*relations_buttons)

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
