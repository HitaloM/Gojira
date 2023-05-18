# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram import Router

from . import inline, popular, start, view


def setup_routers() -> list[Router]:
    return [
        inline.router,
        popular.router,
        start.router,
        view.router,
    ]


__all__ = (
    "inline",
    "popular",
    "start",
    "view",
)
