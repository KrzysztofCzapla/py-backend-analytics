from dataclasses import dataclass, field
from typing import List, Any, Set

from py_backend_analytics.constants import PACKAGE_NAME
from py_backend_analytics.enums import PyBackendAnalyticsDB


@dataclass
class PyBackendAnalyticsInputData:
    db_connection_string: str
    db_type: PyBackendAnalyticsDB = PyBackendAnalyticsDB.SQLITE
    excluded_endpoints: List[str] = field(default_factory=list)
    excluded_path_fragments: List[str] = field(default_factory=list)
    excluded_path_prefixes: Set[str] = field(default_factory=set)
    logger: Any | None = None

    def __post_init__(self):
        if not self.excluded_endpoints:
            self.excluded_endpoints = ["/favicon.ico", "/style.css"]
        if not self.excluded_path_fragments:
            self.excluded_path_fragments = ["static", PACKAGE_NAME]
