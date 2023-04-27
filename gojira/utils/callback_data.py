# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Optional, Union

from aiogram.filters.callback_data import CallbackData


class LanguageCallback(CallbackData, prefix="setlang"):
    lang: str
    chat: str


class StartCallback(CallbackData, prefix="start"):
    menu: str


class GetAnimeCallback(CallbackData, prefix="anime"):
    method: str
    query: Optional[Union[int, str]] = None
    user_id: int
    is_search: bool = False
