from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
from py_backend_analytics.db.constants import (
    DB_TABLE_NAME,
    DBColumns,
    DB_INDEX_SUFFIX,
    TOP_AGGREGATION_LIMIT,
    UNKNOWN,
    DEFAULT_DB_TIMEOUT,
)
from py_backend_analytics.db.models import AnalyticsSummaryFields as F
from py_backend_analytics.models import RequestInfo


class SQLiteDBClient(AbstractDBClient):
    async def insert_request_info(self, model: RequestInfo):
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            await cur.execute(
                f"""INSERT INTO {DB_TABLE_NAME}
                    ({DBColumns.location}, {DBColumns.page}, {DBColumns.source}, {DBColumns.datestamp})
                    VALUES (?, ?, ?, ?)""",
                (model.location, model.page, model.source, model.datestamp),
            )
            await conn.commit()

    async def get_analytics_summary(self) -> dict:
        async with self._get_connection() as conn:
            now = datetime.now(timezone.utc)

            last_month = (now - timedelta(days=30)).isoformat()
            last_year = (now - timedelta(days=365)).isoformat()

            all_time = {
                F.TOP_COUNTRIES: await self._get_top(conn, DBColumns.location),
                F.TOP_PAGES: await self._get_top(conn, DBColumns.page),
                F.TOP_SOURCES: await self._get_top(conn, DBColumns.source),
            }

            month_stats = {
                F.TOP_COUNTRIES: await self._get_top(
                    conn, DBColumns.location, last_month
                ),
                F.TOP_PAGES: await self._get_top(conn, DBColumns.page, last_month),
                F.TOP_SOURCES: await self._get_top(conn, DBColumns.source, last_month),
            }

            year_stats = {
                F.TOP_COUNTRIES: await self._get_top(
                    conn, DBColumns.location, last_year
                ),
                F.TOP_PAGES: await self._get_top(conn, DBColumns.page, last_year),
                F.TOP_SOURCES: await self._get_top(conn, DBColumns.source, last_year),
            }

            recent_query = f"""
                SELECT
                    {DBColumns.location},
                    {DBColumns.page},
                    {DBColumns.source},
                    {DBColumns.datestamp}
                FROM {DB_TABLE_NAME}
                ORDER BY {DBColumns.datestamp} DESC
                LIMIT 100
            """

            cur = await conn.execute(recent_query)
            recent_rows = await cur.fetchall()

            recent_requests = [
                {
                    F.LOCATION: row[0],
                    F.PAGE: row[1],
                    F.SOURCE: row[2],
                    F.DATESTAMP: row[3],
                }
                for row in recent_rows
            ]

            return {
                F.ALL_TIME: all_time,
                F.LAST_MONTH: month_stats,
                F.LAST_YEAR: year_stats,
                F.RECENT_REQUESTS: recent_requests,
            }

    async def _create_db_table(self):
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            await cur.execute(
                f"""CREATE TABLE {DB_TABLE_NAME}(
                        {DBColumns.id} INTEGER PRIMARY KEY,
                        {DBColumns.location} TEXT NULL,
                        {DBColumns.page} TEXT NOT NULL,
                        {DBColumns.source} TEXT NULL,
                        {DBColumns.datestamp} TEXT NOT NULL
                ) STRICT"""
            )
            await cur.execute(
                f"""CREATE INDEX {DBColumns.datestamp}{DB_INDEX_SUFFIX}
                    ON {DB_TABLE_NAME}({DBColumns.datestamp})"""
            )

    async def _db_table_exists(self) -> bool:
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            result = await cur.execute(
                f"""
                SELECT name
                FROM sqlite_schema
                WHERE type = 'table' AND name = '{DB_TABLE_NAME}'
                """
            )
            name = await result.fetchone()
            return name is not None

    @staticmethod
    async def _get_top(
        conn,
        column: str,
        min_date: str | None = None,
        limit: int = TOP_AGGREGATION_LIMIT,
    ) -> list[dict]:
        query = f"""
            SELECT {column}, COUNT(*) as count
            FROM {DB_TABLE_NAME}
        """
        params = []

        if min_date:
            query += f" WHERE {DBColumns.datestamp} >= ?"
            params.append(min_date)

        query += f"""
            GROUP BY {column}
            ORDER BY count DESC
            LIMIT {limit}
        """

        cur = await conn.execute(query, params)
        rows = await cur.fetchall()

        return [
            {
                F.VALUE: row[0] or UNKNOWN,
                F.COUNT: row[1],
            }
            for row in rows
        ]

    @asynccontextmanager
    async def _get_connection(self):
        import aiosqlite

        connection = await aiosqlite.connect(
            self._connection_string, timeout=DEFAULT_DB_TIMEOUT
        )
        try:
            yield connection
        finally:
            await connection.close()
