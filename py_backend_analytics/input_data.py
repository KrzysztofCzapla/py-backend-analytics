from dataclasses import dataclass, field
from typing import List, Any, Set

from py_backend_analytics.enums import PyBackendAnalyticsDB


@dataclass
class PyBackendAnalyticsInputData:
    db_connection_string: str
    db_type: PyBackendAnalyticsDB = PyBackendAnalyticsDB.SQLITE
    excluded_endpoints: List[str] = field(default_factory=list)
    excluded_path_fragments: List[str] = field(default_factory=list)
    excluded_path_prefixes: Set[str] = field(default_factory=set)
    logger: Any | None = None
