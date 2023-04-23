# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.filters.callback_data import CallbackData


class LanguageCallback(CallbackData, prefix="setlang"):
    lang: str
    chat: str


class StartCallback(CallbackData, prefix="start"):
    menu: str
