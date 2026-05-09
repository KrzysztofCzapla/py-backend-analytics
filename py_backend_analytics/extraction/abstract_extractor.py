from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from py_backend_analytics.models import RequestInfo

T = TypeVar("T")


class AbstractExtractor(ABC, Generic[T]):
    @abstractmethod
    def extract(self, request: T) -> RequestInfo: ...
