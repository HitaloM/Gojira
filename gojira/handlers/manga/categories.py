# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from gojira import AniList
from gojira.utils.callback_data import (
    MangaCallback,
    MangaCategCallback,
    MangaGCategCallback,
    StartCallback,
)
from gojira.utils.keyboard_pagination import Pagination

router = Router(name="manga_categories")


@router.callback_query(MangaCategCallback.filter())
async def manga_categories(callback: CallbackQuery, callback_data: MangaCategCallback):
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
        item_data=lambda i, pg: MangaGCategCallback(page=pg, categorie=i).pack(),
        item_title=lambda i, pg: categories[i],
        page_data=lambda pg: MangaCategCallback(page=pg).pack(),
    )

    keyboard = layout.create(page, lines=5, columns=2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=StartCallback(menu="manga").pack(),
        )
    )

    with suppress(TelegramAPIError):
        await message.edit_text(
            _("Below are the categories of <b>manga</b>, choose one to see the results:"),
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(MangaGCategCallback.filter())
async def manga_categorie(callback: CallbackQuery, callback_data: MangaGCategCallback):
    message = callback.message
    if not message:
        return

    categorie = callback_data.categorie
    page = callback_data.page

    status, data = await AniList.categories("manga", page, categorie)
    if data["data"]:
        items = data["data"]["Page"]["media"]
        results = []
        for item in items:
            results.append(item)

        layout = Pagination(
            results,
            item_data=lambda i, pg: MangaCallback(query=i["id"]).pack(),
            item_title=lambda i, pg: i["title"]["romaji"],
            page_data=lambda pg: MangaGCategCallback(page=pg, categorie=categorie).pack(),
        )

        keyboard = layout.create(1, lines=8)

        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"),
                callback_data=MangaCategCallback(page=page).pack(),
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
