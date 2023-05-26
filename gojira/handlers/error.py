# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import html

from aiogram import Router
from aiogram.types import ErrorEvent

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
    if not message:
        return

    exception = error.exception

    chat_id = message.chat.id
    err_tlt = type(exception).__name__
    err_msg = str(exception)

    if await cache.get(f"error:{chat_id}") == err_msg:
        return

    conn_errors = (
        "TelegramNetworkError",
        "TelegramAPIError",
        "RestartingTelegram",
    )
    if err_tlt in conn_errors:
        log.error("Connection/API error detected!", exc_info=error.exception)
        return

    ignored_errors = (
        "TelegramBadRequest",
        "TelegramRetryAfter",
    )
    if err_tlt in ignored_errors:
        return

    log.warn("Update that caused the error:\n %s", message, exc_info=error.exception)

    text = "<b>Sorry, I encountered a error!</b>\n"
    text += (
        f"<code>{html.escape(err_tlt, quote=False)}: {html.escape(err_msg, quote=False)}</code>"
    )
    await cache.set(f"error:{chat_id}", err_msg, "1h")
    await bot.send_message(chat_id, text)
