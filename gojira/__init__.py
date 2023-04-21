# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n

from gojira.config import config

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()
i18n = I18n(path="locales", default_locale="en", domain="bot")
