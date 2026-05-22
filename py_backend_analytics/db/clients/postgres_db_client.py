from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
from py_backend_analytics.db.constants import (
    DB_TABLE_NAME,
    DBColumns,
    DB_INDEX_SUFFIX,
    TOP_AGGREGATION_LIMIT,
    UNKNOWN,
)
from py_backend_analytics.db.models import AnalyticsSummaryFields as F
from py_backend_analytics.models import RequestInfo


class PostgresDBClient(AbstractDBClient):
    async def insert_request_info(self, model: RequestInfo):
        async with self._get_connection() as conn:
            await conn.execute(
                f"""
                INSERT INTO {DB_TABLE_NAME}
                ({DBColumns.location}, {DBColumns.page}, {DBColumns.source}, {DBColumns.datestamp})
                VALUES ($1, $2, $3, $4)
                """,
                model.location,
                model.page,
                model.source,
                model.datestamp,
            )

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

            rows = await conn.fetch(
                f"""
                SELECT
                    {DBColumns.location},
                    {DBColumns.page},
                    {DBColumns.source},
                    {DBColumns.datestamp}
                FROM {DB_TABLE_NAME}
                ORDER BY {DBColumns.datestamp} DESC
                LIMIT 100
                """
            )

            recent_requests = [
                {
                    F.LOCATION: r[0],
                    F.PAGE: r[1],
                    F.SOURCE: r[2],
                    F.DATESTAMP: r[3],
                }
                for r in rows
            ]

            return {
                F.ALL_TIME: all_time,
                F.LAST_MONTH: month_stats,
                F.LAST_YEAR: year_stats,
                F.RECENT_REQUESTS: recent_requests,
            }

    async def _create_db_table(self):
        async with self._get_connection() as conn:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
                    {DBColumns.id} SERIAL PRIMARY KEY,
                    {DBColumns.location} TEXT NULL,
                    {DBColumns.page} TEXT NOT NULL,
                    {DBColumns.source} TEXT NULL,
                    {DBColumns.datestamp} TIMESTAMPTZ NOT NULL
                )
                """
            )

            await conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {DBColumns.datestamp}{DB_INDEX_SUFFIX}
                ON {DB_TABLE_NAME} ({DBColumns.datestamp})
                """
            )

    async def _db_table_exists(self) -> bool:
        async with self._get_connection() as conn:
            row = await conn.fetchrow(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = $1
                """,
                DB_TABLE_NAME,
            )
            return row is not None

    @staticmethod
    async def _get_top(
        conn,
        column: str,
        min_date: str | None = None,
        limit: int = TOP_AGGREGATION_LIMIT,
    ) -> list[dict]:
        if min_date:
            query = f"""
                SELECT {column}, COUNT(*) AS count
                FROM {DB_TABLE_NAME}
                WHERE {DBColumns.datestamp} >= $1
                GROUP BY {column}
                ORDER BY count DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, min_date, limit)
        else:
            query = f"""
                SELECT {column}, COUNT(*) AS count
                FROM {DB_TABLE_NAME}
                GROUP BY {column}
                ORDER BY count DESC
                LIMIT $1
            """
            rows = await conn.fetch(query, limit)

        return [
            {
                F.VALUE: r[0] or UNKNOWN,
                F.COUNT: r[1],
            }
            for r in rows
        ]

    @asynccontextmanager
    async def _get_connection(self):
        if self._pool is not None:
            async with self._pool.acquire() as conn:
                yield conn
        else:
            import asyncpg

            conn = await asyncpg.connect(self._connection_string)
            try:
                yield conn
            finally:
                await conn.close()
