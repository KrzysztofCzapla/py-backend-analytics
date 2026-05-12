from collections import defaultdict
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


async def fastapi_get_visualization_page(
    app: FastAPI, input_data: PyBackendAnalyticsInputData, request: Request
) -> _TemplateResponse:
    app.mount(
        "/analytics-static", StaticFiles(directory=_STATIC_DIR), name="analytics-static"
    )

    db_client = await get_db_client(input_data.db_connection_string, input_data.db_type)

    results = await db_client.read_request_info()
    # requests = _normalize_datetimes(results)

    # page_counter = Counter(r.page for r in requests)
    # source_counter = Counter(r.source for r in requests)
    # location_counter = Counter(r.location for r in requests)
    #
    # months = Counter((r.datestamp.year, r.datestamp.month) for r in requests)
    # years = Counter(r.datestamp.year for r in requests)
    # hours = Counter(r.datestamp.hour for r in requests)
    #
    # top_month = months.most_common(1)[0] if months else None
    # top_year = years.most_common(1)[0] if years else None
    #
    # daily, weekly = _build_time_series(requests)

    return results
