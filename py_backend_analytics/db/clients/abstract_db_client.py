from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

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
        if not await self.db_table_exists():
            await self.create_db_table()

    @abstractmethod
    async def insert_request_info(self, model: RequestInfo): ...

    @abstractmethod
    async def read_request_info(self) -> List[RequestInfo]: ...

    @abstractmethod
    async def create_db_table(self): ...

    @abstractmethod
    async def db_table_exists(self) -> bool: ...
