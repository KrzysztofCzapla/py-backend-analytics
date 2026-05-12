from dataclasses import dataclass
from datetime import datetime


@dataclass
class RequestInfo:
    page: str
    source: str
    datestamp: datetime
    location: str | None = None
