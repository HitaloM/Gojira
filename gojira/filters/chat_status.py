# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatIsPrivate(BaseFilter):
    """Check if the chat is ChatType.PRIVATE."""

    async def __call__(self, message: Message):
        return message.chat.type == ChatType.PRIVATE
