from datetime import datetime, timezone

from fastapi.routing import Match

from py_backend_analytics.extraction.extractors.abstract_extractor import (
    AbstractExtractor,
    T,
)
from py_backend_analytics.models import RequestInfo


class FastAPIExtractor(AbstractExtractor):
    def extract(self, request: T) -> RequestInfo:
        """Extracts info from a FastAPI request. No FastAPI typing, so FastAPI is not needed at import."""
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
        try:
            if self.geo_lookup is not None:
                location = self.geo_lookup.get_country(ip)
            else:
                location = None
        except Exception as e:
            location = None
            if self.logger:
                try:
                    self.logger.warning(
                        f"Got an error while trying to get an ip location: {e}"
                    )
                except Exception as e:
                    pass
        return RequestInfo(
            location=location, page=page, source=source, datestamp=datestamp
        )
