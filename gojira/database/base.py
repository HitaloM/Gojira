from tortoise import Tortoise


async def connect_database():
    await Tortoise.init(
        db_url="sqlite://gojira/database/db.sqlite3",
        modules={"models": ["gojira.database.models"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas()
