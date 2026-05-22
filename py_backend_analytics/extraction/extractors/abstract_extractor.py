from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

from py_backend_analytics.extraction.geo_lookup import IpCountryLookup
from py_backend_analytics.models import RequestInfo

T = TypeVar("T")


class AbstractExtractor(ABC, Generic[T]):
    geo_lookup: IpCountryLookup | None

    def __init__(self, logger: Any = None):
        self.logger = logger
        try:
            self.geo_lookup = IpCountryLookup()
        except Exception as e:
            self.geo_lookup = None
            if self.logger is not None:
                try:
                    self.logger.warning(f"Could not init IpCountryLookup: {e}")
                except Exception as e:
                    pass

    @abstractmethod
    def extract(self, request: T) -> RequestInfo: ...
