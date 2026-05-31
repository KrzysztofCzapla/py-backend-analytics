from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Tuple

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
from py_backend_analytics.db.constants import (
    DB_TABLE_NAME,
    DBColumns,
    DB_INDEX_SUFFIX,
    TOP_AGGREGATION_LIMIT,
    UNKNOWN,
)
from py_backend_analytics.db.models import (
    AnalyticsSummaryFields as F,
    AnalyticsSummaryFields,
)
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
            return {
                F.ALL_TIME: await self._get_stats(conn, F.ALL_TIME),
                F.LAST_MONTH: await self._get_stats(conn, F.LAST_MONTH),
                F.LAST_YEAR: await self._get_stats(conn, F.LAST_YEAR),
                F.LAST_24_HOURS: await self._get_stats(conn, F.LAST_24_HOURS),
            }

    async def _get_stats(self, conn, time_name: str) -> dict:
        bucket_str, date = await self._get_bucket_str_and_date(time_name)
        return {
            F.TOP_COUNTRIES: await self._get_top(conn, DBColumns.location, date),
            F.TOP_PAGES: await self._get_top(conn, DBColumns.page, date),
            F.TOP_SOURCES: await self._get_top(conn, DBColumns.source, date),
            F.BUCKET: await self._get_bucket(conn, bucket_str, date),
        }

    @staticmethod
    async def _get_bucket(
        conn, bucket_str: str, min_date: datetime | None = None
    ) -> list[dict]:
        if min_date:
            query = f"""
                SELECT {bucket_str}, COUNT(*) as visits
                FROM {DB_TABLE_NAME}
                WHERE {DBColumns.datestamp} >= $1
                GROUP BY bucket
                ORDER BY bucket;
                """
            rows = await conn.fetch(query, min_date)
        else:
            query = f"""
                SELECT {bucket_str}, COUNT(*) as visits
                FROM {DB_TABLE_NAME}
                GROUP BY bucket
                ORDER BY bucket;
                """
            rows = await conn.fetch(query)
        return [
            {
                F.VALUE: str(row[0]).replace("+00:00", "") or UNKNOWN,
                F.COUNT: row[1],
            }
            for row in rows
        ]

    @staticmethod
    async def _get_top(
        conn,
        column: str,
        min_date: datetime | None = None,
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

    @staticmethod
    async def _get_bucket_str_and_date(time_name: str) -> Tuple[str, str | None]:
        now = datetime.now(timezone.utc)

        last_year = now - timedelta(days=365)
        last_month = now - timedelta(days=30)
        last_24 = now - timedelta(days=1)

        return {
            AnalyticsSummaryFields.ALL_TIME: (
                f"date_trunc('month', {DBColumns.datestamp}) AS bucket",
                None,
            ),
            AnalyticsSummaryFields.LAST_YEAR: (
                f"date_trunc('month', {DBColumns.datestamp}) AS bucket",
                last_year,
            ),
            AnalyticsSummaryFields.LAST_MONTH: (
                f"date_trunc('day', {DBColumns.datestamp}) AS bucket",
                last_month,
            ),
            AnalyticsSummaryFields.LAST_24_HOURS: (
                f"date_trunc('hour', {DBColumns.datestamp}) AS bucket",
                last_24,
            ),
        }[time_name]

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
