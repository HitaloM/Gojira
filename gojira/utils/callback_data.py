# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Optional, Union

from aiogram.filters.callback_data import CallbackData


class LanguageCallback(CallbackData, prefix="setlang"):
    lang: str
    chat: str


class StartCallback(CallbackData, prefix="start"):
    menu: str


class AnimeCallback(CallbackData, prefix="anime"):
    query: Union[int, str]
    user_id: Optional[int] = None
    is_search: bool = False


class AnimeDescCallback(CallbackData, prefix="anime_description"):
    anime_id: int
    user_id: int
    page: int = 0


class AnimeMoreCallback(CallbackData, prefix="anime_more"):
    anime_id: int
    user_id: int


class AnimeCharCallback(CallbackData, prefix="anime_character"):
    anime_id: int
    user_id: int
    page: int = 0


class AnimeStaffCallback(CallbackData, prefix="anime_staff"):
    anime_id: int
    user_id: int
    page: int = 0


class AnimeAiringCallback(CallbackData, prefix="anime_airing"):
    anime_id: int
    user_id: int


class AnimeStudioCallback(CallbackData, prefix="anime_studio"):
    anime_id: int
    user_id: int
    page: int = 0


class AnimeUpcomingCallback(CallbackData, prefix="anime_upcoming"):
    page: int


class AnimeSuggCallback(CallbackData, prefix="anime_suggestions"):
    page: int
