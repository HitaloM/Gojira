# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio

from tortoise.connection import connections

from gojira import bot, dp, i18n
from gojira.database.base import connect_database
from gojira.handlers import anime, language, pm_menu, users
from gojira.middlewares.acl import ACLMiddleware
from gojira.middlewares.i18n import MyI18nMiddleware
from gojira.utils.command_list import set_ui_commands


async def main():
    await connect_database()

    dp.message.middleware(ACLMiddleware())
    dp.message.middleware(MyI18nMiddleware(i18n=i18n))
    dp.callback_query.middleware(ACLMiddleware())
    dp.callback_query.middleware(MyI18nMiddleware(i18n=i18n))

    dp.include_routers(pm_menu.router)
    dp.include_router(anime.router)
    dp.include_router(language.router)
    dp.include_router(users.router)

    await set_ui_commands(bot)

    useful_updates = dp.resolve_used_update_types()

    await dp.start_polling(bot, allowed_updates=useful_updates)
    await connections.close_all(discard=True)


if __name__ == "__main__":
    asyncio.run(main())
