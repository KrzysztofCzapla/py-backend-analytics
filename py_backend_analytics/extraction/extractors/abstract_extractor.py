from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from py_backend_analytics.extraction.geo_lookup import IpCountryLookup
from py_backend_analytics.models import RequestInfo

T = TypeVar("T")


class AbstractExtractor(ABC, Generic[T]):
    geo_lookup: IpCountryLookup = IpCountryLookup()

    @classmethod
    @abstractmethod
    def extract(cls, request: T) -> RequestInfo: ...
