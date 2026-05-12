from contextlib import asynccontextmanager
from typing import List

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
import aiosqlite

from py_backend_analytics.db.constants import DB_TABLE_NAME, DBColumns, DB_INDEX_SUFFIX
from py_backend_analytics.db.models import Filters
from py_backend_analytics.models import RequestInfo


class SQLiteDBClient(AbstractDBClient):
    async def insert_request_info(self, model: RequestInfo):
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            await cur.execute(
                f"""INSERT INTO {DB_TABLE_NAME}
                    ({DBColumns.location}, {DBColumns.page}, {DBColumns.source}, {DBColumns.datestamp}) VALUES
                    (?, ?, ?, ?)""",
                (model.location, model.page, model.source, model.datestamp),
            )
            await conn.commit()

    async def read_request_info(
        self, filters: Filters | None = None
    ) -> List[RequestInfo]:
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            query = f"""SELECT
                    {DBColumns.location},
                    {DBColumns.page},
                    {DBColumns.source},
                    {DBColumns.datestamp}
                FROM
                    {DB_TABLE_NAME}
            """
            wheres = []
            params = []
            if filters:
                if filters.location:
                    wheres.append(f"{DBColumns.location} = ?")
                    params.append(filters.location)
                if filters.page:
                    wheres.append(f"{DBColumns.page} = ?")
                    params.append(filters.page)
                if filters.source:
                    wheres.append(f"{DBColumns.source} = ?")
                    params.append(filters.source)
                if filters.min_date:
                    wheres.append(f"{DBColumns.datestamp} >= ?")
                    params.append(filters.min_date)
                if filters.max_date:
                    wheres.append(f"{DBColumns.datestamp} <= ?")
                    params.append(filters.max_date)

            if wheres and params:
                query += "WHERE " + " AND ".join(wheres)
            results = await cur.execute(query, params)
            results = await results.fetchall()
            output = []
            for result in results:
                output.append(RequestInfo(*result))
            return output

    async def create_db_table(self):
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
            # datestamp will be the most used column when it comes to filtering
            await cur.execute(
                f"""CREATE INDEX {DBColumns.datestamp}{DB_INDEX_SUFFIX} ON {DB_TABLE_NAME}({DBColumns.datestamp})"""
            )

    async def db_table_exists(self) -> bool:
        async with self._get_connection() as conn:
            cur = await conn.cursor()
            result = await cur.execute(
                f"SELECT name FROM sqlite_schema WHERE type = 'table' AND name = '{DB_TABLE_NAME}'"
            )
            name = await result.fetchone()
            return name is not None

    @asynccontextmanager
    async def _get_connection(self):
        connection = await aiosqlite.connect(self.connection_string)
        yield connection
        await connection.close()
