from dataclasses import dataclass

from py_backend_analytics.enums import PyBackendAnalyticsDB


@dataclass
class PyBackendAnalyticsInputData:
    db_connection_string: str
    db_type: PyBackendAnalyticsDB = PyBackendAnalyticsDB.SQLITE
    excluded_endpoints = None
