# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any

from gojira import cache

from .client import AiohttpBaseClient


class JikanClient(AiohttpBaseClient):
    def __init__(self) -> None:
        self.base_url: str = "https://api.jikan.moe/"
        super().__init__(base_url=self.base_url)

    @cache(ttl="1d")
    async def schedules(self, day: str | None = None) -> tuple[int, dict[str, Any]]:
        return await self._make_request("GET", url=f"/v4/schedules/{day or ""}")
