from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AbstractDBClient(ABC):
    logger: Any

    @abstractmethod
    def insert_request_info(self): ...

    @abstractmethod
    def read_request_info(self): ...

    @abstractmethod
    def create_db_table(self): ...

    @abstractmethod
    def check_db_table_exists(self): ...
