from dataclasses import dataclass, field
from typing import List, Any

from py_backend_analytics.enums import PyBackendAnalyticsDB


@dataclass
class PyBackendAnalyticsInputData:
    db_connection_string: str
    db_type: PyBackendAnalyticsDB = PyBackendAnalyticsDB.SQLITE
    excluded_endpoints: List[str] = field(default_factory=list)
    logger: Any | None = None
