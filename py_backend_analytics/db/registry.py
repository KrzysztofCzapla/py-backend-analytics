from typing import Any

from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
from py_backend_analytics.db.clients.postgres_db_client import PostgresDBClient
from py_backend_analytics.db.clients.sqlite_db_client import SQLiteDBClient
from py_backend_analytics.enums import PyBackendAnalyticsDB

DB_CLIENTS = {
    PyBackendAnalyticsDB.SQLITE: SQLiteDBClient,
    PyBackendAnalyticsDB.POSTGRES: PostgresDBClient,
}


async def get_db_client(
    connection_string: str, connection_pool: Any, db_type: PyBackendAnalyticsDB
) -> AbstractDBClient:
    """Unified interface for getting the correct type of DB Client"""
    db_client_class = DB_CLIENTS.get(db_type)
    if not db_client_class:
        raise ValueError(f"Provided wrong DB type: {db_type}")
    return await db_client_class.create(connection_string, connection_pool)
