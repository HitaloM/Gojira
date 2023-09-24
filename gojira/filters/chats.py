# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Chat, TelegramObject


class ChatTypeFilter(BaseFilter):
    """Filter for chat type."""

    def __init__(self, chat_type: ChatType | tuple[ChatType, ...]):
        self.chat_type = chat_type

    async def __call__(self, event: TelegramObject, event_chat: Chat) -> bool:
        return event_chat.type in self.chat_type
