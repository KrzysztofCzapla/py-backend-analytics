from dataclasses import dataclass
from datetime import datetime


@dataclass
class Filters:
    min_date: datetime | None = None
    max_date: datetime | None = None
    location: str | None = None
    page: str | None = None
    source: str | None = None
