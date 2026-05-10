from datetime import datetime, timezone
from starlette.routing import Match

from py_backend_analytics.extraction.extractors.abstract_extractor import (
    AbstractExtractor,
    T,
)
from py_backend_analytics.models import RequestInfo


class FastAPIExtractor(AbstractExtractor):
    @staticmethod
    def extract(request: T) -> RequestInfo:
        page = request.url.path
        for route in request.app.router.routes:
            match, scope = route.matches(request.scope)

            if match == Match.FULL:
                page = scope["route"].path  # /users/{id} instead of /users/12313
                break
        source = request.headers.get("referer", "direct")
        datestamp = datetime.now(timezone.utc)
        # ip = request.client.host
        location = "France"  # TODO - mock
        return RequestInfo(
            location=location, page=page, source=source, datestamp=datestamp
        )
