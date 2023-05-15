# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from aiogram.filters.callback_data import CallbackData


class LanguageCallback(CallbackData, prefix="setlang"):
    lang: str
    chat: str


class StartCallback(CallbackData, prefix="start"):
    menu: str


class AnimeCallback(CallbackData, prefix="anime"):
    query: int | str
    user_id: int | None = None
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


class AnimePopuCallback(CallbackData, prefix="anime_popular"):
    page: int


class AnimeCategCallback(CallbackData, prefix="anime_categories"):
    page: int


class AnimeGCategCallback(CallbackData, prefix="anime_categorie"):
    page: int
    categorie: str


class MangaCallback(CallbackData, prefix="manga"):
    query: int | str
    user_id: int | None = None
    is_search: bool = False


class MangaMoreCallback(CallbackData, prefix="manga_more"):
    manga_id: int
    user_id: int


class MangaDescCallback(CallbackData, prefix="manga_description"):
    manga_id: int
    user_id: int
    page: int = 0


class MangaCharCallback(CallbackData, prefix="manga_character"):
    manga_id: int
    user_id: int
    page: int = 0


class MangaStaffCallback(CallbackData, prefix="manga_staff"):
    manga_id: int
    user_id: int
    page: int = 0


class MangaUpcomingCallback(CallbackData, prefix="manga_upcoming"):
    page: int


class MangaPopuCallback(CallbackData, prefix="manga_popular"):
    page: int


class MangaCategCallback(CallbackData, prefix="manga_categories"):
    page: int


class MangaGCategCallback(CallbackData, prefix="manga_categorie"):
    page: int
    categorie: str


class CharacterCallback(CallbackData, prefix="character"):
    query: int | str
    user_id: int | None = None
    is_search: bool = False


class CharacterPopuCallback(CallbackData, prefix="character_popular"):
    page: int


class StaffCallback(CallbackData, prefix="staff"):
    query: int | str
    user_id: int | None = None
    is_search: bool = False


class StaffPopuCallback(CallbackData, prefix="staff_popular"):
    page: int
