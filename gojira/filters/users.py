# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from gojira.config import config


class IsAdmin(BaseFilter):
    """Check if user is admin."""

    @staticmethod
    async def __call__(union: Message | CallbackQuery) -> bool:
        is_callback = isinstance(union, CallbackQuery)
        message = union.message if is_callback else union
        if message is None:
            return False

        if message.chat.type == ChatType.PRIVATE:
            return True
        if union.from_user is None:
            return False

        member = await message.chat.get_member(union.from_user.id)
        return member.status in {
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
        }


class IsSudo(BaseFilter):
    """Check if user is sudo."""

    @staticmethod
    async def __call__(union: Message | CallbackQuery) -> bool:
        is_callback = isinstance(union, CallbackQuery)
        message = union.message if is_callback else union
        if message is None:
            return False

        if union.from_user is None:
            return False

        return union.from_user.id in config.sudoers
