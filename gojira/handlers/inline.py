# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import random
from contextlib import suppress

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResult,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

router = Router(name="inline")


@router.inline_query()
async def inline_help(inline: InlineQuery):
    results: list[InlineQueryResult] = [
        InlineQueryResultArticle(
            type="article",
            id=str(random.getrandbits(64)),
            title="!a <anime>",
            input_message_content=InputTextMessageContent(
                message_text="*!a <anime>* is used to search for anime in inline, it can also be \
used in PM to get complete anime information just like `/anime`. command",
                parse_mode=ParseMode.MARKDOWN,
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔨 Run 'anime'",
                            switch_inline_query_current_chat="!a ",
                        )
                    ]
                ]
            ),
            description="Search for anime.",
        ),
        InlineQueryResultArticle(
            type="article",
            id=str(random.getrandbits(64)),
            title="!m <manga>",
            input_message_content=InputTextMessageContent(
                message_text="*!m <manga>* is used to search for manga in inline, it can also be \
used in PM to get complete manga information just like `/manga` command.",
                parse_mode=ParseMode.MARKDOWN,
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔨 Run 'manga'",
                            switch_inline_query_current_chat="!m ",
                        )
                    ]
                ]
            ),
            description="Search for manga.",
        ),
        InlineQueryResultArticle(
            type="article",
            id=str(random.getrandbits(64)),
            title="!c <character>",
            input_message_content=InputTextMessageContent(
                message_text="*!c <character>* is used to search for character in inline, it can \
also be used in PM to get complete character information just like `/character` command.",
                parse_mode=ParseMode.MARKDOWN,
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔨 Run 'character'",
                            switch_inline_query_current_chat="!c ",
                        )
                    ]
                ]
            ),
            description="Search for character.",
        ),
        InlineQueryResultArticle(
            type="article",
            id=str(random.getrandbits(64)),
            title="!s <staff>",
            input_message_content=InputTextMessageContent(
                message_text="*!s <staff>* is used to search for staff in inline, it can also be \
used in PM to get complete staff information just like `/staff` command.",
                parse_mode=ParseMode.MARKDOWN,
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔨 Run 'staff'",
                            switch_inline_query_current_chat="!s ",
                        )
                    ]
                ]
            ),
            description="Search for staff.",
        ),
    ]

    with suppress(TelegramBadRequest):
        await inline.answer(results=results, cache_time=60)
