# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message
from aiogram.utils.i18n import gettext as _

from gojira.database import Chats, Users


async def get_chat_language(
    union: Message | CallbackQuery,
) -> tuple[str | None, list | str | None]:
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return None, None

    if not message or not message.from_user:
        return message.chat.type, None

    language_code = None

    if message.chat.type == ChatType.PRIVATE:
        user = union.from_user
        language_code = await Users.get_language(user=user)

    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        chat = message.chat
        language_code = await Chats.get_language(chat=chat)

    return message.chat.type, language_code


async def i18n_anilist_status(status: str) -> str:
    status_dict = {
        "FINISHED": _("Finished"),
        "RELEASING": _("Releasing"),
        "NOT_YET_RELEASED": _("Not yet released"),
        "CANCELLED": _("Cancelled"),
        "HIATUS": _("Hiatus"),
    }
    return status_dict.get(status, "")


async def i18n_anilist_source(source: str) -> str:
    source_dict = {
        "ORIGINAL": _("Original"),
        "MANGA": _("Manga"),
        "LIGHT_NOVEL": _("Light Novel"),
        "VISUAL_NOVEL": _("Visual Novel"),
        "VIDEO_GAME": _("Video Game"),
        "OTHER": _("Other"),
        "NOVEL": _("Novel"),
        "DOUJINSHI": _("Doujinshi"),
        "ANIME": _("Anime"),
        "WEB_NOVEL": _("Web Novel"),
        "LIVE_ACTION": _("Live Action"),
        "GAME": _("Game"),
        "COMIC": _("Comic"),
        "MULTIMEDIA_PROJECT": _("Multimedia Project"),
        "PICTURE_BOOK": _("Picture Book"),
    }
    return source_dict.get(source, "")


async def i18n_anilist_format(format: str) -> str:
    format_dict = {
        "TV": _("TV"),
        "TV_SHORT": _("TV Short"),
        "MOVIE": _("Movie"),
        "SPECIAL": _("Special"),
        "OVA": _("OVA"),
        "ONA": _("ONA"),
        "MUSIC": _("Music"),
        "MANGA": _("Manga"),
        "NOVEL": _("Novel"),
        "ONE_SHOT": _("One Shot"),
    }
    return format_dict.get(format, "")
