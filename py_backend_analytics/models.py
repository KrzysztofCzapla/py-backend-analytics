from dataclasses import dataclass
from datetime import datetime


@dataclass
class RequestInfo:
    location: str
    page: str
    source: str
    datestamp: datetime
