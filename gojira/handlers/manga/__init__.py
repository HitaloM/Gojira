# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router

from . import categories, inline, popular, start, upcoming, view


def setup_routers() -> list[Router]:
    return [
        start.router,
        view.router,
        inline.router,
        popular.router,
        upcoming.router,
        categories.router,
    ]


__all__ = (
    "categories",
    "inline",
    "popular",
    "start",
    "upcoming",
    "view",
)
