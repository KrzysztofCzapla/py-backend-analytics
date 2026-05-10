from datetime import datetime, timezone

from py_backend_analytics.extraction.abstract_extractor import AbstractExtractor, T
from py_backend_analytics.models import RequestInfo


class FastAPIExtractor(AbstractExtractor):
    @staticmethod
    def extract(request: T) -> RequestInfo:
        page = request.url.page
        source = request.headers.get("referer", "direct")
        datestamp = datetime.now(timezone.utc)
        # ip = request.client.host
        location = "France"  # TODO - mock
        return RequestInfo(
            location=location, page=page, source=source, datestamp=datestamp
        )
