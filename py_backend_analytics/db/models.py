from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyticsSummaryFields:
    # root
    ALL_TIME: str = "all_time"
    LAST_MONTH: str = "last_month"
    LAST_YEAR: str = "last_year"
    RECENT_REQUESTS: str = "recent_requests"

    # TimeRangeStats
    TOP_COUNTRIES: str = "top_countries"
    TOP_PAGES: str = "top_pages"
    TOP_SOURCES: str = "top_sources"

    # TopEntry
    VALUE: str = "value"
    COUNT: str = "count"

    # RequestInfo
    LOCATION: str = "location"
    PAGE: str = "page"
    SOURCE: str = "source"
    DATESTAMP: str = "datestamp"
