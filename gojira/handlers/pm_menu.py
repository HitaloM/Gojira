# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.formatting import TextMention
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira.filters.chats import ChatTypeFilter
from gojira.handlers.anime.view import anime_view
from gojira.handlers.character.view import character_view
from gojira.handlers.manga.view import manga_view
from gojira.handlers.staff.view import staff_view
from gojira.handlers.studio.view import studio_view
from gojira.utils.callback_data import StartCallback

router = Router(name="pm_menu")


@router.message(CommandStart(deep_link=True), ChatTypeFilter(ChatType.PRIVATE))
async def start_command_deep_link(message: Message, command: CommandObject):
    if command.args and len(command.args.split("_")) > 1:
        content_type, *content_id = command.args.split("_")

        if content_type == "anime":
            await anime_view(message, anime_id=int(content_id[0]))
        elif content_type == "malanime":
            await anime_view(message, anime_id=int(content_id[0]), mal=True)
        elif content_type == "manga":
            await manga_view(message, manga_id=int(content_id[0]))
        elif content_type == "character":
            await character_view(message, character_id=int(content_id[0]))
        elif content_type == "staff":
            await staff_view(message, staff_id=int(content_id[0]))
        elif content_type == "studio":
            await studio_view(message, studio_id=int(content_id[0]))
        else:
            await start_command(message)


@router.message(CommandStart(), ChatTypeFilter(ChatType.PRIVATE))
@router.callback_query(StartCallback.filter(F.menu == "start"))
async def start_command(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("ℹ️ About"), callback_data=StartCallback(menu="about"))
    keyboard.button(text=_("🌐 Language"), callback_data=StartCallback(menu="language"))
    keyboard.button(text=_("👮‍♂️ Help"), callback_data=StartCallback(menu="help"))
    keyboard.adjust(2)

    text = _(
        "Hello, {user_name}. I am <b>Gojira</b>, a Telegram bot that can help \
you with informations about anime and manga, such as genres, characters, studios, \
staff. And much more!"
    ).format(user_name=TextMention(union.from_user.full_name, user=union.from_user).as_html())

    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )


@router.message(Command("help"), ChatTypeFilter(ChatType.PRIVATE))
@router.callback_query(StartCallback.filter(F.menu == "help"))
async def help_menu(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message or not union.from_user:
        return

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("👸 Anime"), callback_data=StartCallback(menu="anime"))
    keyboard.button(text=_("📖 Manga"), callback_data=StartCallback(menu="manga"))
    keyboard.button(text=_("👤 Character"), callback_data=StartCallback(menu="character"))
    keyboard.button(text=_("👨‍💻 Staff"), callback_data=StartCallback(menu="staff"))
    keyboard.button(text=_("🎬 Studio"), callback_data=StartCallback(menu="studio"))
    keyboard.adjust(3)

    if is_callback or message.chat.type == ChatType.PRIVATE:
        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    text = _("Click on one of the buttons below to start exploring all my features.")

    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )


@router.message(Command("about"))
@router.callback_query(StartCallback.filter(F.menu == "about"))
async def about(union: Message | CallbackQuery):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    if not message:
        return

    text = _(
        "<b>Gojira</b> is a bot developed using <b>Python</b> that utilizes <b>AIOgram</b> and \
<b>AniList GraphQL API</b> to provide fast, stable and comprehensive information about animes \
and mangas. The name Gojira (ゴジラ) is a reference to the Japanese name of the famous monster \
Godzilla."
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("📦 GitHub"), url="https://github.com/HitaloM/Gojira")
    keyboard.button(text=_("📚 Channel"), url="https://t.me/HitaloProjects")
    keyboard.adjust(2)

    if is_callback or message.chat.type == ChatType.PRIVATE:
        keyboard.row(
            InlineKeyboardButton(
                text=_("🔙 Back"), callback_data=StartCallback(menu="start").pack()
            )
        )

    await (message.edit_text if is_callback else message.reply)(
        text,
        reply_markup=keyboard.as_markup(),
    )
