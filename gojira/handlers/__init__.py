# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.exceptions import AiogramError, DetailedAiogramError

from gojira import dp
from gojira.handlers import (
    anime,
    character,
    doas,
    error,
    inline,
    language,
    manga,
    pm_menu,
    staff,
    studio,
    upcoming,
    user,
    view,
)
from gojira.utils.logging import log


def setup_routers():
    try:
        dp.include_routers(
            error.router,
            view.router,
            pm_menu.router,
            language.router,
            doas.router,
            user.router,
            upcoming.router,
            *anime.setup_routers(),
            *character.setup_routers(),
            *manga.setup_routers(),
            *staff.setup_routers(),
            *studio.setup_routers(),
            inline.router,
        )
    except (AiogramError, DetailedAiogramError):
        log.error("Failed to setup AIOgram routers!", exc_info=True)
