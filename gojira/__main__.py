# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import sys

from cashews.exceptions import CacheBackendInteractionError

from gojira import AniList, bot, cache, dp, i18n
from gojira.handlers import (
    anime,
    character,
    doas,
    error,
    language,
    manga,
    pm_menu,
    staff,
    studio,
    user,
    view,
)
from gojira.middlewares.acl import ACLMiddleware
from gojira.middlewares.i18n import MyI18nMiddleware
from gojira.utils.command_list import set_ui_commands
from gojira.utils.logging import log


async def main():
    try:
        await cache.ping()
    except CacheBackendInteractionError:
        sys.exit(log.critical("Can't connect to RedisDB! Exiting..."))

    dp.message.middleware(ACLMiddleware())
    dp.message.middleware(MyI18nMiddleware(i18n=i18n))
    dp.callback_query.middleware(ACLMiddleware())
    dp.callback_query.middleware(MyI18nMiddleware(i18n=i18n))
    dp.inline_query.middleware(ACLMiddleware())
    dp.inline_query.middleware(MyI18nMiddleware(i18n=i18n))

    dp.include_routers(
        error.router,
        view.router,
        pm_menu.router,
        language.router,
        doas.router,
        user.router,
        *anime.setup_routers(),
        *character.setup_routers(),
        *manga.setup_routers(),
        *staff.setup_routers(),
        *studio.setup_routers(),
    )

    await set_ui_commands(bot, i18n)

    useful_updates = dp.resolve_used_update_types()

    try:
        await dp.start_polling(bot, allowed_updates=useful_updates)
    finally:
        await bot.session.close()

    await AniList.close()
    await cache.clear()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Gojira stopped!")
