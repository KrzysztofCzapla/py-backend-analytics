from py_backend_analytics.db.clients.abstract_db_client import AbstractDBClient
from py_backend_analytics.db.clients.sqlite_db_client import SQLiteDBClient
from py_backend_analytics.enums import PyBackendAnalyticsDB

DB_CLIENTS = {PyBackendAnalyticsDB.SQLITE: SQLiteDBClient}


def get_db_client(
    connection_string: str, db_type: PyBackendAnalyticsDB
) -> AbstractDBClient:
    db_client_class = DB_CLIENTS.get(db_type)
    if not db_client_class:
        raise ValueError(f"Provided wrong DB type: {db_type}")
    return db_client_class(connection_string)
