# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress
from typing import Dict

import aiohttp
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira.utils.anime import ANILIST_API, CATEGORIE_QUERY
from gojira.utils.callback_data import (
    AnimeCallback,
    AnimeCategCallback,
    AnimeGCategCallback,
    StartCallback,
)
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="anime_categories")


@router.callback_query(AnimeCategCallback.filter())
async def anime_categories(callback: CallbackQuery, callback_data: AnimeCategCallback):
    message = callback.message
    if not message:
        return None

    page = callback_data.page

    categories: Dict = {
        "Action": _("Action"),
        "Adventure": _("Adventure"),
        "Comedy": _("Comedy"),
        "Drama": _("Drama"),
        "Ecchi": _("Ecchi"),
        "Fantasy": _("Fantasy"),
        "Horror": _("Horror"),
        "Mahou Shoujo": _("Mahou Shoujo"),
        "Mecha": _("Mecha"),
        "Music": _("Music"),
        "Mystery": _("Mystery"),
        "Psychological": _("Psychological"),
        "Romance": _("Romance"),
        "Sci-Fi": _("Sci-Fi"),
        "Slice of Life": _("Slice of Life"),
        "Sports": _("Sports"),
        "Supernatural": _("Supernatural"),
        "Thriller": _("Thriller"),
    }
    categories_list = sorted(list(categories.keys()))

    layout = Pagination(
        categories_list,
        item_data=lambda i, pg: AnimeGCategCallback(page=pg, categorie=i).pack(),
        item_title=lambda i, pg: categories[i],
        page_data=lambda pg: AnimeCategCallback(page=pg).pack(),
    )

    keyboard = layout.create(page, lines=5, columns=2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=StartCallback(menu="anime").pack(),
        )
    )

    with suppress(TelegramAPIError):
        await message.edit_text(
            _("Below are some categories, choose one and find something you like. 😆"),
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(AnimeGCategCallback.filter())
async def anime_categorie(callback: CallbackQuery, callback_data: AnimeGCategCallback):
    message = callback.message
    if not message:
        return None

    categorie = callback_data.categorie
    page = callback_data.page

    async with aiohttp.ClientSession() as client:
        response = await client.post(
            ANILIST_API,
            json=dict(
                query=CATEGORIE_QUERY,
                variables=dict(
                    page=page,
                    genre=categorie,
                    media="ANIME",
                ),
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        data = await response.json()
        if data["data"]:
            items = data["data"]["Page"]["media"]
            results = []
            for item in items:
                results.append(item)

            layout = Pagination(
                results,
                item_data=lambda i, pg: AnimeCallback(query=i["id"]).pack(),
                item_title=lambda i, pg: i["title"]["romaji"],
                page_data=lambda pg: AnimeGCategCallback(page=pg, categorie=categorie).pack(),
            )

            keyboard = layout.create(1, lines=8)

            keyboard.row(
                InlineKeyboardButton(
                    text=_("🔙 Back"),
                    callback_data=AnimeCategCallback(page=page).pack(),
                )
            )

            text = _("Below are up to <b>50</b> results from the <b>{genre}</b> category.").format(
                genre=categorie
            )
            with suppress(TelegramAPIError):
                await message.edit_text(
                    text,
                    reply_markup=keyboard.as_markup(),
                )
