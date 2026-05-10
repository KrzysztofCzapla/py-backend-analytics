from contextlib import contextmanager
from typing import List

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
import sqlite3

from py_backend_analytics.db.constants import DB_TABLE_NAME, DBColumns
from py_backend_analytics.db.models import Filters
from py_backend_analytics.models import RequestInfo


class SQLiteDBClient(AbstractDBClient):
    def insert_request_info(self, model: RequestInfo):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""INSERT INTO {DB_TABLE_NAME}
                    ({DBColumns.location}, {DBColumns.page}, {DBColumns.source}, {DBColumns.datestamp}) VALUES
                    (?, ?, ?, ?)""",
                (model.location, model.page, model.source, model.datestamp),
            )
            conn.commit()

    def read_request_info(self, filters: Filters | None = None) -> List[RequestInfo]:
        with self._get_connection() as conn:
            cur = conn.cursor()
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
            results = cur.execute(query, params)
            results = results.fetchall()
            output = []
            for result in results:
                output.append(RequestInfo(*result))
            return output

    def create_db_table(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""CREATE TABLE {DB_TABLE_NAME}(
                        {DBColumns.id} INTEGER PRIMARY KEY,
                        {DBColumns.location} TEXT NOT NULL,
                        {DBColumns.page} TEXT NOT NULL,
                        {DBColumns.source} TEXT NOT NULL,
                        {DBColumns.datestamp} TEXT NOT NULL
                ) STRICT"""
            )

    def db_table_exists(self) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            result = cur.execute(
                f"SELECT name FROM sqlite_schema WHERE type = 'table' AND name = '{DB_TABLE_NAME}'"
            )
            name = result.fetchone()
            return name is not None

    @contextmanager
    def _get_connection(self):
        connection = sqlite3.connect(self.connection_string)
        yield connection
        connection.close()
