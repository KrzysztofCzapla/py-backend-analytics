from py_backend_analytics.db.clients.sqlite_db_client import SQLiteDBClient
from py_backend_analytics.enums import PyBackendAnalyticsDB

DB_CLIENTS = {PyBackendAnalyticsDB.SQLITE: SQLiteDBClient}
