# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import logging

from tortoise.connection import connections

from gojira import bot, dp, i18n
from gojira.database.base import connect_database
from gojira.handlers import pm_menu
from gojira.middlewares.acl import ACLMiddleware
from gojira.middlewares.i18n import MyI18nMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    await connect_database()

    dp.message.middleware(ACLMiddleware())
    dp.message.middleware(MyI18nMiddleware(i18n=i18n))

    dp.include_routers(pm_menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await connections.close_all(discard=True)


if __name__ == "__main__":
    asyncio.run(main())
