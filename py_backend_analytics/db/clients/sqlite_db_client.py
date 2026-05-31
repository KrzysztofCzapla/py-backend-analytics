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
    DEFAULT_DB_TIMEOUT,
)
from py_backend_analytics.db.models import (
    AnalyticsSummaryFields as F,
    AnalyticsSummaryFields,
)
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
        conn, bucket_str: str, min_date: str | None = None
    ) -> list[dict]:
        where = f"WHERE {DBColumns.datestamp} >= '{min_date}'"
        query = f"""
        SELECT {bucket_str}, COUNT(*) as visits
        FROM {DB_TABLE_NAME}
        {where if min_date else ''}
        GROUP BY bucket
        ORDER BY bucket;
        """
        cur = await conn.execute(query)
        rows = await cur.fetchall()
        return [
            {
                F.VALUE: row[0] or UNKNOWN,
                F.COUNT: row[1],
            }
            for row in rows
        ]

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

    @staticmethod
    async def _get_bucket_str_and_date(time_name: str) -> Tuple[str, str | None]:
        now = datetime.now(timezone.utc)

        last_year = (now - timedelta(days=365)).isoformat()
        last_month = (now - timedelta(days=30)).isoformat()
        last_24 = (now - timedelta(days=1)).isoformat()

        return {
            AnalyticsSummaryFields.ALL_TIME: (
                f"strftime('%Y-%m', {DBColumns.datestamp}) AS bucket",
                None,
            ),
            AnalyticsSummaryFields.LAST_YEAR: (
                f"strftime('%Y-%m', {DBColumns.datestamp}) AS bucket",
                last_year,
            ),
            AnalyticsSummaryFields.LAST_MONTH: (
                f"strftime('%m-%d', {DBColumns.datestamp}) AS bucket",
                last_month,
            ),
            AnalyticsSummaryFields.LAST_24_HOURS: (
                f"strftime('%m-%d %H:00:00', {DBColumns.datestamp}) AS bucket",
                last_24,
            ),
        }[time_name]

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
