from contextlib import contextmanager

from py_backend_analytics.db.abstract_db_client import AbstractDBClient
import sqlite3

from py_backend_analytics.db.constants import DB_TABLE_NAME, DBColumns


class SQLiteDBClient(AbstractDBClient):
    def insert_request_info(self): ...

    def read_request_info(self): ...

    def create_db_table(self):
        with self._get_cursor() as cur:
            cur.execute(
                f"""CREATE TABLE {DB_TABLE_NAME}(
                        {DBColumns.id} INTEGER PRIMARY KEY ASC,
                        {DBColumns.location} TEXT NOT NULL,
                        {DBColumns.page} TEXT NOT NULL,
                        {DBColumns.source} TEXT NOT NULL,
                        {DBColumns.datestamp} TEXT NOT NULL,
                ) STRICT"""
            )

    def db_table_exists(self) -> bool:
        with self._get_cursor() as cur:
            result = cur.execute(
                f"SELECT name FROM sqlite_schema WHERE type = 'table' AND name = '{DB_TABLE_NAME}'"
            )
            name = result.fetchone()
            return name is not None

    @contextmanager
    def _get_cursor(self):
        connection = sqlite3.connect(self.connection_string)
        yield connection.cursor()
        connection.close()


a = SQLiteDBClient(connection_string="mydb.sql", logger=None)
with a._get_cursor() as c:
    x = c.execute(
        f"INSERT INTO {DB_TABLE_NAME} VALUES ('kurwa', 'kurwa', 'kurwa', 'kurwa')"
    )
    x = c.execute(f"select * from {DB_TABLE_NAME}")
    x = x.fetchall()
print(x)
