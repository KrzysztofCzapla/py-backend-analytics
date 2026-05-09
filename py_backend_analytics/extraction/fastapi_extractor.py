from py_backend_analytics.extraction.abstract_extractor import AbstractExtractor, T
from py_backend_analytics.models import RequestInfo


class FastAPIExtractor(AbstractExtractor):
    def extract(self, request: T) -> RequestInfo:
        pass
