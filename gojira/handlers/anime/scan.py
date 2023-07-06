# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress
from datetime import timedelta

from aiogram import Router
from aiogram.enums import ChatType, InputMediaType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Document, InputMediaPhoto, Message, Video
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gojira import TraceMoe, bot, cache
from gojira.utils.callback_data import AnimeCallback

router = Router(name="anime_scan")


@router.message(Command("scan"))
async def anime_scan(message: Message):
    user = message.from_user
    if not message or not user:
        return

    reply = message.reply_to_message

    me = await bot.get_me()
    if user == me:
        return

    if not reply:
        await message.reply(_("Reply to a message with a media."))
        return

    media = (
        reply.photo[-1]
        if reply.photo
        else reply.sticker
        if reply.sticker
        else reply.animation
        if reply.animation
        else reply.document
        if reply.document
        else reply.video
        if reply.video
        else None
    )

    if not media:
        await message.reply(_("No media was found in this message."))
        return

    if isinstance(media, Document | Video):
        if media.thumbnail:
            media = media.thumbnail
        else:
            return

    sent = await message.reply_photo(
        "https://i.imgur.com/m0N2pFc.jpg", caption="Scanning media..."
    )

    file_id = media.file_id

    file = await bot.get_file(file_id)
    if not file or not file.file_path:
        await sent.edit_text(_("File not found."))
        return

    file = await bot.download_file(file.file_path)
    if not file:
        await sent.edit_text(_("Something went wrong while downloading the file."))
        return

    status, data = await TraceMoe.search(file=file)

    if status == 200:
        pass
    elif status == 429:
        await sent.edit_text(_("Excessive use of the API, please try again later."))
        return
    else:
        await sent.edit_text(_("The API is unavailable, please try again later."))
        return

    results = data["result"]
    if len(results) == 0:
        await sent.edit_text(_("No results found."))
        return

    result = results[0]

    video = result["video"]
    to_time = result["to"]
    episode = result["episode"]
    anilist_id = result["anilist"]["id"]
    file_name = result["filename"]
    from_time = result["from"]
    similarity = result["similarity"]
    is_adult = result["anilist"]["isAdult"]
    title_native = result["anilist"]["title"]["native"]
    title_romaji = result["anilist"]["title"]["romaji"]

    text = f"<b>{title_romaji}</b>"
    if title_native:
        text += f" (<code>{title_native}</code>)"
    text += _("\n\n<b>ID</b>: <code>{anime_id}</code>").format(anime_id=anilist_id)
    if episode:
        text += _("\n<b>Episode</b>: <code>{episode}</code>").format(episode=episode)
    if is_adult:
        text += _("\n<b>Adult</b>: <code>Yes</code>")
    text += _("\n<b>Similarity</b>: <code>{similarity}%</code>").format(
        similarity=round(similarity * 100, 2)
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=_("👓 View more"), callback_data=AnimeCallback(query=anilist_id))
    sent = await sent.edit_media(
        InputMediaPhoto(
            type=InputMediaType.PHOTO,
            media=f"https://img.anili.st/media/{anilist_id}",
            caption=text,
        ),
        reply_markup=keyboard.as_markup(),
    )

    from_time = str(timedelta(seconds=result["from"])).split(".", 1)[0].rjust(8, "0")
    to_time = str(timedelta(seconds=result["to"])).split(".", 1)[0].rjust(8, "0")

    if video is not None:
        with suppress(TelegramBadRequest):
            cached_video = await cache.get(f"trace_moe:{video}")
            video = cached_video if cached_video else f"{video}&size=l"

            sent_video = await reply.reply_video(
                video=video,
                caption=(
                    f"<code>{file_name}</code>\n\n<code>{from_time}</code> - \
<code>{to_time}</code>"
                ),
            )

            if sent_video.chat.type != ChatType.PRIVATE:
                keyboard.button(text=_("📹 Preview"), url=sent_video.get_url())
                await bot.edit_message_reply_markup(
                    chat_id=sent.chat.id,  # type: ignore[arg-type]
                    message_id=sent.message_id,  # type: ignore[arg-type]
                    reply_markup=keyboard.as_markup(),
                )

            if not cached_video:
                await cache.set(f"trace_moe:{video}", sent_video.video, expire="1d")
