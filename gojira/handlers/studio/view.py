# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import AniList, bot
from gojira.handlers.studio.start import studio_start
from gojira.utils.callback_data import StudioCallback, StudioMediaCallback

router = Router(name="studio_view")


@router.message(Command("studio"))
@router.callback_query(StudioCallback.filter())
async def studio_view(
    union: Message | CallbackQuery,
    command: CommandObject | None = None,
    callback_data: StudioCallback | None = None,
    studio_id: int | None = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    if isinstance(message, InaccessibleMessage):
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

    if command and not command.args:
        if is_private:
            await studio_start(message)
            return
        await message.reply(
            _("You need to specify an studio. Use <code>/studio name</code> or <code>id</code>")
        )
        return

    query = str(
        callback_data.query
        if is_callback and callback_data is not None
        else command.args
        if command and command.args
        else studio_id
    )
    is_search = callback_data.is_search if is_callback and callback_data else None

    if is_callback and callback_data is not None:
        user_id = callback_data.user_id
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                return

        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    keyboard = InlineKeyboardBuilder()
    if not query.isdecimal():
        _status, data = await AniList.search("studio", query)
        if not data:
            await message.reply(_("No results found."))
            return

        results = data["data"]["Page"]["studios"]
        if results is None or len(results) == 0:
            await message.reply(_("No results found."))
            return

        if len(results) == 1:
            studio_id = int(results[0]["id"])
        else:
            for result in results:
                keyboard.row(
                    InlineKeyboardButton(
                        text=result["name"],
                        callback_data=StudioCallback(
                            query=result["id"],
                            user_id=user.id,
                            is_search=True,
                        ).pack(),
                    )
                )
            await message.reply(
                _("Search results for: <b>{query}</b>").format(query=query),
                reply_markup=keyboard.as_markup(),
            )
            return
    else:
        studio_id = int(query)

    _status, data = await AniList.get("studio", studio_id)
    if not data:
        await message.reply(_("No results found."))
        return

    studio = data["data"]["Studio"]
    if studio is None:
        await union.answer(
            _("No results found."),
            show_alert=True,
            cache_time=60,
        )
        return

    text = f"<b>{studio["name"]}</b>"
    text += _("\n<b>ID</b>: <code>{id}</code>").format(id=studio["id"])
    text += _("\n<b>Favourites</b>: <code>{favourites}</code>").format(
        favourites=studio["favourites"]
    )
    is_anim = _("Yes") if studio["isAnimationStudio"] else _("No")
    text += _("\n<b>Animation Studio</b>: <code>{is_anim}</code>").format(is_anim=is_anim)

    keyboard.button(
        text=_("🎬 Medias"),
        callback_data=StudioMediaCallback(
            studio_name=studio["name"], studio_id=studio["id"], user_id=user.id, page=0
        ),
    )
    keyboard.button(text=_("🐢 AniList"), url=studio["siteUrl"])
    keyboard.adjust(2)

    await (message.edit_text if is_callback and not is_search else message.answer)(
        text,
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(StudioMediaCallback.filter())
async def studio_media_view(callback: CallbackQuery, callback_data: StudioMediaCallback):
    message = callback.message
    user = callback.from_user
    if not message or not user:
        return

    if isinstance(message, InaccessibleMessage):
        return

    studio_id = callback_data.studio_id
    user_id = callback_data.user_id
    page = callback_data.page
    studio_name = callback_data.studio_name

    if user_id != user.id:
        await callback.answer(
            _("This button is not for you"),
            show_alert=True,
            cache_time=60,
        )
        return

    _status, data = await AniList.get_studio_media(studio_id)

    me = await bot.get_me()
    medias = data["data"]["Studio"]["media"]["nodes"]
    media_list = ""
    for media in medias:
        title = media["title"]["romaji"]
        mid = media["id"]
        media_list += f"\n• <code>{mid}</code> - <a href='https://t.me/{me.username}/?start=anime_{mid}'>{title}</a>"

    media_list = media_list.split("\n")
    media_list = [line for line in media_list if line]
    media_list = [media_list[i : i + 8] for i in range(0, len(media_list), 8)]

    keyboard = InlineKeyboardBuilder()

    pages = len(media_list)
    if page > 0:
        keyboard.button(
            text="◀️",
            callback_data=StudioMediaCallback(
                studio_name=studio_name,
                studio_id=studio_id,
                user_id=user_id,
                page=page - 1,
            ),
        )
    if page + 1 != pages:
        keyboard.button(
            text="▶️",
            callback_data=StudioMediaCallback(
                studio_name=studio_name,
                studio_id=studio_id,
                user_id=user_id,
                page=page + 1,
            ),
        )

    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text=_("🔙 Back"),
            callback_data=StudioCallback(query=studio_id, user_id=user_id).pack(),
        )
    )

    media_list = media_list[page]
    media_list = "\n".join(media_list)

    text = _("Media that <b>{name}</b> has worked on:\n{list}").format(
        name=studio_name, list=media_list
    )

    await message.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=keyboard.as_markup(),
    )
