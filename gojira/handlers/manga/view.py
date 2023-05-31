# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import math

import numpy as np
from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, InputMediaPhoto, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lxml import html

from gojira import AniList, bot
from gojira.handlers.manga.start import manga_start
from gojira.utils.callback_data import (
    MangaCallback,
    MangaCharCallback,
    MangaDescCallback,
    MangaMoreCallback,
    MangaStaffCallback,
)

router = Router(name="manga_view")


@router.message(Command("manga"))
@router.callback_query(MangaCallback.filter())
async def manga_view(
    union: Message | CallbackQuery,
    command: CommandObject | None = None,
    callback_data: MangaCallback | None = None,
    manga_id: int | None = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    if command and not command.args:
        if message.chat.type == ChatType.PRIVATE:
            await manga_start(message)
            return
        await message.reply(_("You need to specify an manga. Use /manga name or id"))
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

    query = str(
        callback_data.query
        if is_callback and callback_data is not None
        else command.args
        if command and command.args
        else manga_id
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

    keyboard = InlineKeyboardBuilder()
    if not query.isdecimal():
        status, data = await AniList.search("manga", query)
        if not data:
            await message.reply(_("No results found."))
            return

        results = data["data"]["Page"]["media"]
        if not results or len(results) == 0:
            await message.reply(_("No results found."))
            return

        if len(results) == 1:
            manga_id = int(results[0]["id"])
        else:
            for result in results:
                keyboard.row(
                    InlineKeyboardButton(
                        text=result["title"]["romaji"],
                        callback_data=MangaCallback(
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
        manga_id = int(query)

    status, data = await AniList.get("manga", manga_id)
    if not data:
        await message.reply(_("No results found."))
        return

    if not data["data"]["Page"]["media"]:
        await message.reply(_("No results found."))
        return

    manga = data["data"]["Page"]["media"][0]

    if not manga:
        await union.answer(
            _("No results found."),
            show_alert=True,
            cache_time=60,
        )
        return

    photo = f"https://img.anili.st/media/{manga_id}"

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
    text += _("\n\n<b>ID</b>: <code>{id}</code>").format(id=manga["id"])
    if manga["format"]:
        text += _("\n<b>Format</b>: <code>{format}</code>").format(format=manga["format"])
    if manga["volumes"]:
        text += _("\n<b>Volumes</b>: <code>{volumes}</code>").format(volumes=manga["volumes"])
    if manga["chapters"]:
        text += _("\n<b>Chapters</b>: <code>{chapters}</code>").format(chapters=manga["chapters"])
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

    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(
            text=_("👓 View More"),
            callback_data=MangaMoreCallback(
                manga_id=manga_id,
                user_id=user.id,
            ).pack(),
        )
    )

    if "relations" in manga and len(manga["relations"]["edges"]) > 0:
        relations_buttons = []
        for relation in manga["relations"]["edges"]:
            if relation["relationType"] in ["PREQUEL", "SEQUEL"]:
                button_text = (
                    _("➡️ Sequel") if relation["relationType"] == "SEQUEL" else _("⬅️ Prequel")
                )
                relations_buttons.append(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=MangaCallback(
                            query=relation["node"]["id"],
                            user_id=user.id,
                        ).pack(),
                    )
                )
        if len(relations_buttons) > 0:
            if relations_buttons[0].text != "⬅️ Prequel":
                relations_buttons.reverse()
            keyboard.row(*relations_buttons)

    if bool(message.photo) and is_callback:
        await message.edit_media(
            InputMediaPhoto(type="photo", media=photo, caption=text),
            reply_markup=keyboard.as_markup(),
        )
        return
    if bool(message.photo) and not bool(message.via_bot):
        await message.edit_text(
            text,
            reply_markup=keyboard.as_markup(),
        )
        return

    await message.answer_photo(
        photo,
        caption=text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(MangaMoreCallback.filter())
async def manga_more(callback: CallbackQuery, callback_data: MangaMoreCallback):
    message = callback.message
    user = callback.from_user
    if not message:
        return

    manga_id = callback_data.manga_id
    user_id = callback_data.user_id
    manga_url = f"https://anilist.co/manga/{manga_id}"

    if user_id != user.id:
        await callback.answer(
            _("This button is not for you"),
            show_alert=True,
            cache_time=60,
        )
        return

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text=_("📜 Description"),
        callback_data=MangaDescCallback(manga_id=manga_id, user_id=user_id),
    )
    keyboard.button(
        text=_("🧑‍🤝‍🧑 Characters"),
        callback_data=MangaCharCallback(manga_id=manga_id, user_id=user_id),
    )
    keyboard.button(
        text=_("👨‍💻 Staff"),
        callback_data=MangaStaffCallback(manga_id=manga_id, user_id=user_id),
    )

    keyboard.button(text=_("🐢 AniList"), url=manga_url)
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=MangaCallback(
                query=manga_id,
                user_id=user.id,
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


@router.callback_query(MangaDescCallback.filter())
async def manga_description(callback: CallbackQuery, callback_data: MangaDescCallback):
    message = callback.message
    user = callback.from_user
    if not message:
        return

    manga_id = callback_data.manga_id
    user_id = callback_data.user_id
    page = callback_data.page

    if user_id != user.id:
        await callback.answer(
            _("This button is not for you"),
            show_alert=True,
            cache_time=60,
        )
        return

    status, data = await AniList.get_adesc("manga", manga_id)
    manga = data["data"]["Page"]["media"][0]

    if not manga["description"]:
        await callback.answer(
            _("This manga does not have a description."),
            show_alert=True,
            cache_time=60,
        )
        return

    description = manga["description"]
    amount = 1024
    page = 1 if page <= 0 else page
    offset = (page - 1) * amount
    stop = offset + amount
    pages = math.ceil(len(description) / amount)
    description = description[offset - (3 if page > 1 else 0) : stop]

    page_buttons = []
    if page > 1:
        page_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=MangaDescCallback(
                    manga_id=manga_id, user_id=user_id, page=page - 1
                ).pack(),
            )
        )

    if page != pages:
        description = description[: len(description) - 3] + "..."
        page_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=MangaDescCallback(
                    manga_id=manga_id, user_id=user_id, page=page + 1
                ).pack(),
            )
        )

    keyboard = InlineKeyboardBuilder()
    if len(page_buttons) > 0:
        keyboard.row(*page_buttons)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=MangaMoreCallback(
                manga_id=manga_id,
                user_id=user_id,
            ).pack(),
        )
    )

    parsed_html = html.fromstring(description.replace("<br>", ""))
    description = (
        str(html.tostring(parsed_html, encoding="unicode")).replace("<p>", "").replace("</p>", "")
    )

    await message.edit_caption(
        caption=description,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(MangaCharCallback.filter())
async def manga_characters(callback: CallbackQuery, callback_data: MangaCharCallback):
    message = callback.message
    user = callback.from_user
    if not message:
        return

    manga_id = callback_data.manga_id
    user_id = callback_data.user_id
    page = callback_data.page

    if user_id != user.id:
        await callback.answer(
            _("This button is not for you"),
            show_alert=True,
            cache_time=60,
        )
        return

    status, data = await AniList.get_achars("manga", manga_id)
    manga = data["data"]["Page"]["media"][0]

    if not manga["characters"]:
        await callback.answer(
            _("This manga does not have characters."),
            show_alert=True,
            cache_time=60,
        )
        return

    characters_text = ""
    characters = sorted(
        [
            {
                "id": character["node"]["id"],
                "name": character["node"]["name"],
                "role": character["role"],
            }
            for character in manga["characters"]["edges"]
        ],
        key=lambda x: x["id"],
    )

    me = await bot.get_me()
    for character in characters:
        characters_text += f"\n• <code>{character['id']}</code> - <a href='https://t.me/\
{me.username}/?start=character_{character['id']}'>{character['name']['full']}</a> \
(<i>{character['role']}</i>)"

    # Separate staff_text into pages of 8 items
    characters_text = np.array(characters_text.split("\n"))
    characters_text = np.delete(characters_text, np.argwhere(characters_text == ""))
    characters_text = np.split(characters_text, np.arange(8, len(characters_text), 8))

    pages = len(characters_text)

    page_buttons = []
    if page > 0:
        page_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=MangaCharCallback(
                    manga_id=manga_id, user_id=user_id, page=page - 1
                ).pack(),
            )
        )
    if page + 1 != pages:
        page_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=MangaCharCallback(
                    manga_id=manga_id, user_id=user_id, page=page + 1
                ).pack(),
            )
        )

    characters_text = characters_text[page].tolist()
    characters_text = "\n".join(characters_text)

    keyboard = InlineKeyboardBuilder()
    if len(page_buttons) > 0:
        keyboard.add(*page_buttons)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=MangaMoreCallback(
                manga_id=manga_id,
                user_id=user_id,
            ).pack(),
        )
    )

    text = _("Below are some characters from the item in question.")
    text = f"{text}\n\n{characters_text}"
    await message.edit_caption(
        caption=text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(MangaStaffCallback.filter())
async def manga_staff(callback: CallbackQuery, callback_data: MangaStaffCallback):
    message = callback.message
    user = callback.from_user
    if not message:
        return

    manga_id = callback_data.manga_id
    user_id = callback_data.user_id
    page = callback_data.page

    if user_id != user.id:
        await callback.answer(
            _("This button is not for you"),
            show_alert=True,
            cache_time=60,
        )
        return

    status, data = await AniList.get_astaff("manga", manga_id)
    anime = data["data"]["Page"]["media"][0]

    if not anime["staff"]:
        await callback.answer(
            _("This anime does not have staff."),
            show_alert=True,
            cache_time=60,
        )
        return

    staff_text = ""
    staffs = sorted(
        [
            {
                "id": staff["node"]["id"],
                "name": staff["node"]["name"],
                "role": staff["role"],
            }
            for staff in anime["staff"]["edges"]
        ],
        key=lambda x: x["id"],
    )

    me = await bot.get_me()
    for person in staffs:
        staff_text += f"\n• <code>{person['id']}</code> - <a href='https://t.me/{me.username}/\
?start=staff_{person['id']}'>{person['name']['full']}</a> (<i>{person['role']}</i>)"

    # Separate staff_text into pages of 8 items
    staff_text = np.array(staff_text.split("\n"))
    staff_text = np.delete(staff_text, np.argwhere(staff_text == ""))
    staff_text = np.split(staff_text, np.arange(8, len(staff_text), 8))

    pages = len(staff_text)

    page_buttons = []
    if page > 0:
        page_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=MangaStaffCallback(
                    manga_id=manga_id, user_id=user_id, page=page - 1
                ).pack(),
            )
        )
    if page + 1 != pages:
        page_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=MangaStaffCallback(
                    manga_id=manga_id, user_id=user_id, page=page + 1
                ).pack(),
            )
        )

    staff_text = staff_text[page].tolist()
    staff_text = "\n".join(staff_text)

    keyboard = InlineKeyboardBuilder()
    if len(page_buttons) > 0:
        keyboard.add(*page_buttons)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=MangaMoreCallback(
                manga_id=manga_id,
                user_id=user_id,
            ).pack(),
        )
    )

    text = _("Below are some persons from the item in question.")
    text = f"{text}\n\n{staff_text}"
    await message.edit_caption(
        caption=text,
        reply_markup=keyboard.as_markup(),
    )
