# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import AniList
from gojira.handlers.staff.start import staff_start
from gojira.utils.callback_data import StaffCallback

router = Router(name="staff_view")


@router.message(Command("staff"))
@router.callback_query(StaffCallback.filter())
async def staff_view(
    union: Message | CallbackQuery,
    command: CommandObject | None = None,
    callback_data: StaffCallback | None = None,
    staff_id: int | None = None,
):
    is_callback = isinstance(union, CallbackQuery)
    message = union.message if is_callback else union
    user = union.from_user
    if not message or not user:
        return

    is_private: bool = message.chat.type == ChatType.PRIVATE

    if command and not command.args:
        if is_private:
            await staff_start(message)
            return
        await message.reply(_("You need to specify an staff. Use /staff name or id"))
        return

    query = str(
        callback_data.query
        if is_callback and callback_data is not None
        else command.args
        if command and command.args
        else staff_id
    )

    if is_callback and callback_data is not None:
        user_id = callback_data.user_id
        if user_id is not None:
            user_id = int(user_id)

            if user_id != user.id:
                return

        is_search = callback_data.is_search
        if bool(is_search) and not is_private:
            await message.delete()

    if not bool(query):
        return

    keyboard = InlineKeyboardBuilder()
    if not query.isdecimal():
        status, data = await AniList.search("staff", query)
        if not data:
            await message.reply(_("No results found."))
            return

        results = data["data"]["Page"]["staff"]
        if results is None or len(results) == 0:
            await message.reply(_("No results found."))
            return

        if len(results) == 1:
            staff_id = int(results[0]["id"])
        else:
            for result in results:
                keyboard.row(
                    InlineKeyboardButton(
                        text=result["name"]["full"],
                        callback_data=StaffCallback(
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
        staff_id = int(query)

    status, data = await AniList.get("staff", staff_id)
    if not data:
        await message.reply(_("No results found."))
        return

    staff = data["data"]["Page"]["staff"][0]
    if staff is None:
        await union.answer(
            _("No results found."),
            show_alert=True,
            cache_time=60,
        )
        return

    text = f"**{staff['name']['full']}**"
    text += _("\n**ID**: `{id}`").format(id=staff["id"])
    if staff["language"]:
        text += _("\n**Language**: `{language}`").format(language=staff["language"])
    if staff["favourites"]:
        text += _("\n**Favourites**: `{favourites}`").format(favourites=staff["favourites"])
    if staff["description"]:
        text += f"\n\n{staff['description']}"

    photo: str = ""
    if image := staff["image"]:
        if large_image := image["large"]:
            photo = large_image
        elif medium_image := image["medium"]:
            photo = medium_image

    keyboard.button(text=_("🐢 AniList"), url=staff["siteUrl"])

    keyboard.adjust(2)

    if len(text) > 1024:
        text = text[:1021] + "..."

    # Markdown
    text = text.replace("__", "**")
    text = text.replace("~", "||")

    if len(photo) > 0:
        await message.answer_photo(
            photo=photo,
            caption=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard.as_markup(),
        )
    else:
        await message.answer(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard.as_markup(),
        )
