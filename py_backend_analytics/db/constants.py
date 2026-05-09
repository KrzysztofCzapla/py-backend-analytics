from dataclasses import dataclass

from py_backend_analytics.constants import PACKAGE_NAME

DB_TABLE_NAME = f"{PACKAGE_NAME}_requests_info"


@dataclass(frozen=True)
class DBColumns:
    id = "id"
    location = "location"
    page = "page"
    source = "source"
    datestamp = "datestamp"
