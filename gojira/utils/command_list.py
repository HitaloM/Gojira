# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)
from aiogram.utils.i18n import I18n


async def set_ui_commands(bot: Bot, i18n: I18n):
    _ = i18n.gettext

    with suppress(TelegramRetryAfter):
        await bot.delete_my_commands()
        for lang in i18n.available_locales:
            all_chats_commands: list[BotCommand] = [
                BotCommand(
                    command="anime",
                    description=_("Get anime informations.", locale=lang),
                ),
                BotCommand(
                    command="manga",
                    description=_("Get manga informations.", locale=lang),
                ),
                BotCommand(
                    command="character",
                    description=_("Get character informations.", locale=lang),
                ),
                BotCommand(
                    command="staff",
                    description=_("Get staff informations.", locale=lang),
                ),
                BotCommand(
                    command="studio",
                    description=_("Get studio informations.", locale=lang),
                ),
                BotCommand(
                    command="scan",
                    description=_("Try to identify the source anime of a media", locale=lang),
                ),
                BotCommand(
                    command="user",
                    description=_("Get AniList user informations.", locale=lang),
                ),
                BotCommand(
                    command="language",
                    description=_("Change bot language.", locale=lang),
                ),
                BotCommand(
                    command="about",
                    description=_("About the bot.", locale=lang),
                ),
            ]

            user_commands: list[BotCommand] = [
                BotCommand(
                    command="start",
                    description=_("Start the bot.", locale=lang),
                ),
                BotCommand(
                    command="help",
                    description=_("Get help.", locale=lang),
                ),
            ] + all_chats_commands

            group_commands: list[
                BotCommand
            ] = all_chats_commands  # this will be changed in the future with new commands

            await bot.set_my_commands(
                user_commands,
                BotCommandScopeAllPrivateChats(type="all_private_chats"),
                language_code=lang.split("_")[0].lower() if "_" in lang else lang,
            )

            await bot.set_my_commands(
                group_commands,
                BotCommandScopeAllGroupChats(type="all_group_chats"),
                language_code=lang.split("_")[0].lower() if "_" in lang else lang,
            )
