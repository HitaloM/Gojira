# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from typing import Any, BinaryIO

from gojira import cache

from .client import AiohttpBaseClient


class TraceMoeClient(AiohttpBaseClient):
    def __init__(self) -> None:
        self.base_url: str = "https://api.trace.moe"
        super().__init__(base_url=self.base_url)

    @cache(ttl="1h")
    async def search(self, file: bytes | BinaryIO) -> tuple[int, dict[str, Any]]:
        return await self._make_request(
            method="POST",
            url="/search?anilistInfo&cutBorders",
            data={"image": file},
        )
