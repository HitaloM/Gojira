# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Hitalo M. <https://github.com/HitaloM>

from pathlib import Path
from types import TracebackType
from typing import Any, TypeVar

import aiosqlite

from gojira import app_dir
from gojira.utils.logging import log

T = TypeVar("T")
DB_PATH: Path = app_dir / "gojira/database/db.sqlite3"


class SqliteDBConn:
    def __init__(self, db_name: Path = DB_PATH) -> None:
        self.db_name = db_name

    async def __aenter__(self) -> aiosqlite.Connection:
        self.conn = await aiosqlite.connect(self.db_name)
        self.conn.row_factory = aiosqlite.Row
        return self.conn

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.conn.close()
        if exc_val:
            raise exc_val


class SqliteConnection:
    @staticmethod
    async def __make_request(
        sql: str,
        params: list[tuple] | tuple = (),
        fetch: bool = False,
        mult: bool = False,
    ) -> Any:
        async with SqliteDBConn(DB_PATH) as conn:
            try:
                cursor = (
                    await conn.executemany(sql, params)
                    if isinstance(params, list)
                    else await conn.execute(sql, params)
                )
            except BaseException:
                log.error(
                    "Error executing SQL query!",
                    sql_query=sql,
                    sql_params=params,
                    exc_info=True,
                )
            else:
                if fetch:
                    return await cursor.fetchall() if mult else await cursor.fetchone()
                await conn.commit()

    @staticmethod
    def _convert_to_model(data: dict, model: type[T]) -> T:
        return model(**data)

    @staticmethod
    async def _make_request(
        sql: str,
        params: tuple = (),
        fetch: bool = False,
        mult: bool = False,
        model_type: type[T] | None = None,
    ) -> T | list[T] | str | None:
        raw = await SqliteConnection.__make_request(sql, params, fetch, mult)
        if raw is None:
            return [] if mult else None
        if mult:
            return (
                [SqliteConnection._convert_to_model(i, model_type) for i in raw]
                if model_type is not None
                else list(raw)
            )
        return (
            SqliteConnection._convert_to_model(raw, model_type) if model_type is not None else raw
        )


async def create_tables() -> None:
    await SqliteConnection._make_request(
        sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            language_code TEXT
        );
        """,
    )
    await SqliteConnection._make_request(
        sql="""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY,
            language_code TEXT
        );
        """,
    )
    await SqliteConnection._make_request(sql="PRAGMA journal_mode=WAL")
    await SqliteConnection._make_request(sql="VACUUM")
