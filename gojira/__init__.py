# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n

from gojira.config import config
from gojira.utils.logging import log

__version__ = "1.0.0"

log.info(f"Starting Gojira... | Version: {__version__}")

app_dir: Path = Path(__file__).parent.parent
locales_dir = app_dir / "locales"

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
dp = Dispatcher()
i18n = I18n(path=locales_dir, default_locale="en", domain="bot")
