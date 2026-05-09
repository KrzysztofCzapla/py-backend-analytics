from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AbstractDBClient(ABC):
    connection_string: str
    logger: Any

    def __post_init__(self):
        if not self.db_table_exists():
            self.create_db_table()

    @abstractmethod
    def insert_request_info(self): ...

    @abstractmethod
    def read_request_info(self): ...

    @abstractmethod
    def create_db_table(self): ...

    @abstractmethod
    def db_table_exists(self) -> bool: ...
