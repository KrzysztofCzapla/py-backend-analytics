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
ANALYTICS_STATIC = "static"  # TODO change


async def fastapi_get_visualization_page(
    app: FastAPI, input_data: PyBackendAnalyticsInputData, request: Request
) -> _TemplateResponse:
    app.mount(
        f"/{ANALYTICS_STATIC}",
        StaticFiles(directory=_STATIC_DIR),
        name=ANALYTICS_STATIC,
    )

    db_client = await get_db_client(input_data.db_connection_string, input_data.db_type)

    results = await db_client.get_analytics_summary()

    return _TEMPLATES.TemplateResponse(
        request=request, name="visualization.html", context=results
    )
