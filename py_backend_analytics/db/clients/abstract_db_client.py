from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from py_backend_analytics.models import RequestInfo


@dataclass
class AbstractDBClient(ABC):
    """Client for interaction with the DB. Methods names are very self-descriptive"""

    _connection_string: str | None = None
    _pool: Any = None

    def __post_init__(self):
        if not self._connection_string and not self._pool:
            raise ValueError("Either connection_string or pool must be provided")

    @classmethod
    async def create(cls, connection_string: str, connection_pool: Any):
        self = cls(connection_string, connection_pool)
        await self.db_setup()
        return self

    async def db_setup(self):
        if not await self._db_table_exists():
            await self._create_db_table()

    @abstractmethod
    async def insert_request_info(self, model: RequestInfo): ...

    @abstractmethod
    async def get_analytics_summary(self) -> dict: ...

    @abstractmethod
    async def _create_db_table(self): ...

    @abstractmethod
    async def _db_table_exists(self) -> bool: ...
