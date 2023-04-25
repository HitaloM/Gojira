# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import List

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from gojira import i18n


async def set_ui_commands(bot: Bot):
    commands: List = []

    for lang in i18n.available_locales:
        if "_" in lang:
            lang = lang.split("_")[1].lower()

        commands.extend(
            [
                (
                    [
                        BotCommand(
                            command="start",
                            description=i18n.gettext("Start the bot.", locale=lang),
                        ),
                        BotCommand(
                            command="language",
                            description=i18n.gettext(
                                "Change bot language.", locale=lang
                            ),
                        ),
                    ],
                    BotCommandScopeAllPrivateChats(type="all_private_chats"),
                    lang,
                ),
            ]
        )

    await bot.delete_my_commands()
    for commands_list, scope, lang in commands:
        await bot.set_my_commands(commands_list, scope=scope, language_code=lang)
