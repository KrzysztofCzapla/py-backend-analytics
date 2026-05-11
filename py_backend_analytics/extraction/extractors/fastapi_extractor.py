from datetime import datetime, timezone
from starlette.routing import Match

from py_backend_analytics.extraction.extractors.abstract_extractor import (
    AbstractExtractor,
    T,
)
from py_backend_analytics.models import RequestInfo


class FastAPIExtractor(AbstractExtractor):
    @classmethod
    def extract(cls, request: T) -> RequestInfo:
        page = request.url.path  # /users/12313 - backup
        # best effort to get /users/{id} instead of /users/12313
        for route in request.app.router.routes:
            match, scope = route.matches(request.scope)

            if match == Match.FULL:
                page = scope["route"].path
                break
        source = request.headers.get("referer", "direct")
        datestamp = datetime.now(timezone.utc)
        ip = request.client.host
        location = cls.geo_lookup.get_country(ip)
        return RequestInfo(
            location=location, page=page, source=source, datestamp=datestamp
        )
