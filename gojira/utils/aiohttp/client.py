# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

import asyncio
import ssl
from collections.abc import Callable
from typing import Any

import backoff
import orjson
from aiohttp import ClientError, ClientSession, TCPConnector
from yarl import URL

from gojira.utils.logging import log

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]


class AiohttpBaseClient:
    def __init__(self, base_url: str | URL) -> None:
        self._base_url = base_url
        self._session: ClientSession | None = None
        self.json_loads: _JsonLoads = orjson.loads
        self.json_dumps: _JsonDumps = lambda obj: orjson.dumps(obj).decode()

    async def _get_session(self) -> ClientSession:
        if self._session is None:
            ssl_context = ssl.SSLContext()
            connector = TCPConnector(ssl_context=ssl_context)
            self._session = ClientSession(
                base_url=self._base_url,
                connector=connector,
                json_serialize=self.json_dumps,
            )

        return self._session

    @backoff.on_exception(backoff.expo, ClientError, max_tries=2)
    async def _make_request(
        self,
        method: str,
        url: str | URL,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
    ) -> tuple[int, dict[str, Any]]:
        session = await self._get_session()

        log.debug(
            "AIOHTTP: Making request...",
            request=method,
            url=url,
            json=json,
            params=params,
        )
        async with session.request(method, url, params=params, json=json, data=data) as response:
            status = response.status
            result = await response.json(loads=self.json_loads)

        log.debug(
            "AIOHTTP: Got response.",
            response=method,
            url=url,
            status=status,
            result=result,
        )
        return status, result

    async def close(self) -> None:
        if not self._session:
            log.debug("There's not session to close.")
            return

        if self._session.closed:
            log.debug("Session already closed.")
            return

        await self._session.close()
        log.debug("Session successfully closed.")

        # Wait 250 ms for the underlying SSL connections to close
        # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        await asyncio.sleep(0.250)
