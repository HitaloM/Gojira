# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any

from aiogram import Router
from aiogram.types import Update

router = Router(name="users")


@router.message()
async def handler(update: Update) -> Any:
    pass
