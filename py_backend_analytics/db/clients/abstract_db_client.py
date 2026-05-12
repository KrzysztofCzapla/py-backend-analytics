from abc import ABC, abstractmethod
from dataclasses import dataclass

from py_backend_analytics.models import RequestInfo


@dataclass
class AbstractDBClient(ABC):
    connection_string: str

    @classmethod
    async def create(cls, connection_string: str):
        self = cls(connection_string)
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
