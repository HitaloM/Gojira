# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any

from gojira import cache
from gojira.utils.graphql import (
    AIRING_QUERY,
    ANIME_GET,
    ANIME_SEARCH,
    CATEGORIE_QUERY,
    CHARACTER_GET,
    CHARACTER_POPULAR_QUERY,
    CHARACTER_QUERY,
    CHARACTER_SEARCH,
    DESCRIPTION_QUERY,
    MANGA_GET,
    MANGA_SEARCH,
    POPULAR_QUERY,
    STAFF_GET,
    STAFF_POPULAR_QUERY,
    STAFF_QUERY,
    STAFF_SEARCH,
    STUDIO_GET,
    STUDIO_MEDIA_QUERY,
    STUDIO_POPULAR_QUERY,
    STUDIO_SEARCH,
    STUDIOS_QUERY,
    TRAILER_QUERY,
    UPCOMING_QUERY,
    USER_ANIME_QUERY,
    USER_GET,
    USER_MANGA_QUERY,
    USER_SEARCH,
)

from .client import AiohttpBaseClient


class AniListClient(AiohttpBaseClient):
    def __init__(self) -> None:
        self.base_url: str = "https://graphql.anilist.co"
        super().__init__(base_url=self.base_url)

    @cache(ttl="1h")
    async def search(
        self, media: str, query: str
    ) -> tuple[int, dict[str, Any]] | tuple[None, None]:
        if media.lower() == "character":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": CHARACTER_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        if media.lower() == "anime":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": ANIME_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        if media.lower() == "manga":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": MANGA_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        if media.lower() == "staff":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STAFF_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        if media.lower() == "studio":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STUDIO_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        if media.lower() == "user":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": USER_SEARCH,
                    "variables": {
                        "search": query,
                    },
                },
            )
        return None, None

    @cache(ttl="1h")
    async def get(self, media: str, id: int) -> tuple[int, dict[str, Any]] | tuple[None, None]:
        if media.lower() == "character":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": CHARACTER_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        if media.lower() == "anime":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": ANIME_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        if media.lower() == "manga":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": MANGA_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        if media.lower() == "staff":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STAFF_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        if media.lower() == "studio":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STUDIO_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        if media.lower() == "user":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": USER_GET,
                    "variables": {
                        "id": id,
                    },
                },
            )
        return None, None

    @cache(ttl="1h")
    async def get_adesc(self, media: str, id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": DESCRIPTION_QUERY,
                "variables": {
                    "id": id,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def get_achars(self, media: str, id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": CHARACTER_QUERY,
                "variables": {
                    "id": id,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def get_astaff(self, media: str, id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": STAFF_QUERY,
                "variables": {
                    "id": id,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def get_airing(self, anime_id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": AIRING_QUERY,
                "variables": {
                    "id": anime_id,
                },
            },
        )

    @cache(ttl="1h")
    async def get_astudios(self, media: str, id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": STUDIOS_QUERY,
                "variables": {
                    "id": id,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def get_atrailer(self, media: str, id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": TRAILER_QUERY,
                "variables": {
                    "id": id,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def upcoming(self, media: str) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": UPCOMING_QUERY,
                "variables": {
                    "per_page": 50,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def popular(self, media: str) -> tuple[int, dict[str, Any]]:
        if media.lower() == "character":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": CHARACTER_POPULAR_QUERY,
                },
            )

        if media.lower() == "staff":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STAFF_POPULAR_QUERY,
                },
            )

        if media.lower() == "studio":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": STUDIO_POPULAR_QUERY,
                },
            )

        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": POPULAR_QUERY,
                "variables": {
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def categories(
        self, media: str, page: int, categorie: str
    ) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": CATEGORIE_QUERY,
                "variables": {
                    "page": page,
                    "genre": categorie,
                    "media": media.upper(),
                },
            },
        )

    @cache(ttl="1h")
    async def get_studio_media(self, studio_id: int) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": STUDIO_MEDIA_QUERY,
                "variables": {
                    "id": studio_id,
                },
            },
        )

    @cache(ttl="1h")
    async def get_user_stat(self, user_id: int, stat_type: str) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            "POST",
            url="/",
            json={
                "query": USER_ANIME_QUERY if stat_type.lower() == "anime" else USER_MANGA_QUERY,
                "variables": {
                    "id": user_id,
                },
            },
        )
