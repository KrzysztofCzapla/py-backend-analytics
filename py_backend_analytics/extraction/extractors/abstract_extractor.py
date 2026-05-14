from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from py_backend_analytics.extraction.geo_lookup import IpCountryLookup
from py_backend_analytics.models import RequestInfo

T = TypeVar("T")


class AbstractExtractor(ABC, Generic[T]):
    geo_lookup: IpCountryLookup

    def __init__(self):
        self.geo_lookup = IpCountryLookup()

    @abstractmethod
    def extract(self, request: T) -> RequestInfo: ...
