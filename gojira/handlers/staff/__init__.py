# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router

from . import inline, popular, start, view


def setup_routers() -> list[Router]:
    return [
        start.router,
        view.router,
        inline.router,
        popular.router,
    ]


__all__ = (
    "inline",
    "popular",
    "start",
    "view",
)
