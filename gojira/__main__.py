# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n
from tortoise.connection import connections

from gojira.config import config
from gojira.database.base import connect_database
from gojira.handlers import pm_menu
from gojira.middlewares.i18n import MyI18nMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    await connect_database()
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="en", domain="bot")
    dp.message.middleware(MyI18nMiddleware(i18n=i18n))

    dp.include_routers(pm_menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await connections.close_all(discard=True)


if __name__ == "__main__":
    asyncio.run(main())
