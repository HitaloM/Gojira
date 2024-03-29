# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import html

from aiogram import Router
from aiogram.types import CallbackQuery, ErrorEvent

from gojira import bot, cache
from gojira.utils.logging import log

router = Router(name="error")


@router.errors()
async def errors_handler(error: ErrorEvent):
    update = error.update
    message = (
        getattr(update, "message", None)
        or getattr(update, "callback_query", None)
        or getattr(update, "edited_message", None)
    )
    is_callback = isinstance(message, CallbackQuery)
    message = message.message if is_callback else message
    if not message:
        return

    exception = error.exception

    chat_id = message.chat.id
    err_tlt = type(exception).__name__
    err_msg = str(exception)

    cached_error = await cache.get(f"error:{chat_id}")
    if cached_error == err_msg:
        return

    conn_errors = (
        "TelegramNetworkError",
        "TelegramAPIError",
        "RestartingTelegram",
    )
    if err_tlt in conn_errors:
        log.error("Connection/API error detected!", error=err_msg, exc_info=error.exception)
        return

    log.error("Error detected!", update=message, error=err_msg, exc_info=error.exception)

    text = "<b>Sorry, I encountered a error!</b>\n"
    text += (
        f"<code>{html.escape(err_tlt, quote=False)}: {html.escape(err_msg, quote=False)}</code>"
    )
    if not cached_error:
        await cache.set(f"error:{chat_id}", err_msg, "1h")
    await bot.send_message(chat_id, text)
