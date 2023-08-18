# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira import AniList
from gojira.utils.callback_data import (
    AnimeCallback,
    AnimeCategCallback,
    AnimeGCategCallback,
    StartCallback,
)
from gojira.utils.keyboard import Pagination

router = Router(name="anime_categories")


@router.callback_query(AnimeCategCallback.filter())
async def anime_categories(callback: CallbackQuery, callback_data: AnimeCategCallback):
    message = callback.message
    if not message:
        return

    page = callback_data.page

    categories: dict = {
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
    categories_list = sorted(categories.keys())

    layout = Pagination(
        categories_list,
        item_data=lambda i, pg: AnimeGCategCallback(page=pg, categorie=i).pack(),
        item_title=lambda i, _: categories.get(i, ""),
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
            _("Below are the categories of <b>anime</b>, choose one to see the results:"),
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(AnimeGCategCallback.filter())
async def anime_categorie(callback: CallbackQuery, callback_data: AnimeGCategCallback):
    message = callback.message
    if not message:
        return

    categorie = callback_data.categorie
    page = callback_data.page

    status, data = await AniList.categories("anime", page, categorie)

    if data["data"]:
        items = data["data"]["Page"]["media"]
        results = [item.copy() for item in items]

        layout = Pagination(
            results,
            item_data=lambda i, _: AnimeCallback(query=i["id"]).pack(),
            item_title=lambda i, _: i["title"]["romaji"],
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
