import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n

from gojira.config import config
from gojira.handlers import pm_menu
from gojira.middlewares.i18n import MyI18nMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="en", domain="bot")
    dp.message.middleware(MyI18nMiddleware(i18n=i18n))

    dp.include_routers(pm_menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
