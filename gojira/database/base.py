# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022-2023 Hitalo M. <https://github.com/HitaloM>

from tortoise import Tortoise


async def connect_database():
    await Tortoise.init(
        db_url="sqlite://gojira/database/db.sqlite3",
        modules={"models": ["gojira.database.models"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
