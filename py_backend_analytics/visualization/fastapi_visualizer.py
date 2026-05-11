from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates, _TemplateResponse

from py_backend_analytics.db.registry import get_db_client
from py_backend_analytics.input_data import PyBackendAnalyticsInputData


_TEMPLATES_DIR = Path(__file__).parent / "templates"
_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATES = Jinja2Templates(directory=_TEMPLATES_DIR)


def _normalize_datetimes(requests):
    for r in requests:
        dt = r.datestamp

        # parse string
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)

        # make everything UTC-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        r.datestamp = dt

    return requests


def _build_time_series(requests):
    daily = defaultdict(int)
    weekly = defaultdict(int)

    for r in requests:
        d = r.datestamp

        daily[d.date()] += 1

        y, w, _ = d.isocalendar()
        weekly[(y, w)] += 1

    return (
        [{"date": str(k), "count": v} for k, v in sorted(daily.items())],
        [{"week": f"{k[0]}-W{k[1]}", "count": v} for k, v in sorted(weekly.items())],
    )


def fastapi_get_visualization_page(
    app: FastAPI, input_data: PyBackendAnalyticsInputData, request: Request
) -> _TemplateResponse:
    app.mount(
        "/analytics-static", StaticFiles(directory=_STATIC_DIR), name="analytics-static"
    )

    db_client = get_db_client(input_data.db_connection_string, input_data.db_type)

    requests = _normalize_datetimes(db_client.read_request_info())

    page_counter = Counter(r.page for r in requests)
    source_counter = Counter(r.source for r in requests)
    location_counter = Counter(r.location for r in requests)

    months = Counter((r.datestamp.year, r.datestamp.month) for r in requests)
    years = Counter(r.datestamp.year for r in requests)
    hours = Counter(r.datestamp.hour for r in requests)

    top_month = months.most_common(1)[0] if months else None
    top_year = years.most_common(1)[0] if years else None

    daily, weekly = _build_time_series(requests)

    return _TEMPLATES.TemplateResponse(
        "visualization.html",
        {
            "request": request,
            # metrics
            "total_requests": len(requests),
            "unique_pages": len(page_counter),
            "unique_sources": len(source_counter),
            "unique_locations": len(location_counter),
            # rankings
            "top_pages": page_counter.most_common(20),
            "top_sources": source_counter.most_common(20),
            "top_locations": location_counter.most_common(20),
            # time-based stats
            "months": months,
            "years": years,
            "hours": hours,
            "top_month": top_month,
            "top_year": top_year,
            # time series charts
            "daily": daily,
            "weekly": weekly,
            # table
            "latest_requests": sorted(
                requests, key=lambda r: r.datestamp, reverse=True
            )[:100],
        },
    )
