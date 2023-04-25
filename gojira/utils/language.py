# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Literal, Union

from aiogram.enums import ChatType
from aiogram.types import Chat, User

from gojira.database.models import Chats, Users


async def get_chat_language(
    chat: Union[User, Chat]
) -> tuple[str | Literal[ChatType.PRIVATE], str]:
    if isinstance(chat, User) or chat.type == ChatType.PRIVATE:
        lang = await Users.get(id=chat.id)
    else:
        lang = await Chats.get(id=chat.id)

    return ChatType.PRIVATE if isinstance(chat, User) else chat.type, lang.language_code
