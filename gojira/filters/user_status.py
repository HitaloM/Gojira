# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message


class IsAdmin(BaseFilter):
    """Check if user is admin."""

    async def __call__(self, union: Message | CallbackQuery) -> bool:
        is_callback = isinstance(union, CallbackQuery)
        message = union.message if is_callback else union
        if message is None:
            return False

        if message.chat.type == ChatType.PRIVATE:
            return True
        if union.from_user is None:
            return False

        member = await message.chat.get_member(union.from_user.id)
        return member.status in (
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
        )
