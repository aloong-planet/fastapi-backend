from asynch import connect
from asynch.cursors import Cursor

from app.configs import APP_SETTINGS

async def get_clickhouse_session() -> Cursor:
    clickhouse_conn = await connect(
        host=APP_SETTINGS.CLICKHOUSE_HOST,
        port=APP_SETTINGS.CLICKHOUSE_PORT,
        user=APP_SETTINGS.CLICKHOUSE_USER,
        password=APP_SETTINGS.CLICKHOUSE_PASSWORD,
        database=APP_SETTINGS.CLICKHOUSE_DB
    )

    async with clickhouse_conn.cursor() as cursor:
        yield cursor
