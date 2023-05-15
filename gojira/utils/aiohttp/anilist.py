# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any

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
    STAFF_QUERY,
    STUDIOS_QUERY,
    TRAILER_QUERY,
    UPCOMING_QUERY,
)

from .client import AiohttpBaseClient


class AniList(AiohttpBaseClient):
    def __init__(self) -> None:
        self.base_url: str = "https://graphql.anilist.co"
        super().__init__(base_url=self.base_url)

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
        return None, None

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
        return None, None

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

    async def popular(self, media: str) -> tuple[int, dict[str, Any]]:
        if media.lower() == "character":
            return await self._make_request(
                "POST",
                url="/",
                json={
                    "query": CHARACTER_POPULAR_QUERY,
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
