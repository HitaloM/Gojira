# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n
from cashews import cache

from gojira.config import config
from gojira.utils.aiohttp import AniListClient, JikanClient, TraceMoeClient
from gojira.utils.logging import log
from gojira.utils.systools import shell_run

commit_count = asyncio.run(shell_run("git rev-list --count HEAD")) or "None"
commit_hash = asyncio.run(shell_run("git rev-parse --short HEAD")) or "None"
__version__ = f"{commit_hash} ({commit_count})"

log.info("Starting Gojira...", version=__version__)

app_dir: Path = Path(__file__).parent.parent
locales_dir: Path = app_dir / "locales"

cache.setup(f"redis://{config.redis_host}", client_side=True)

# Aiohttp Clients
AniList = AniListClient()
TraceMoe = TraceMoeClient()
Jikan = JikanClient()

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
dp = Dispatcher()
i18n = I18n(path=locales_dir, default_locale="en", domain="bot")
