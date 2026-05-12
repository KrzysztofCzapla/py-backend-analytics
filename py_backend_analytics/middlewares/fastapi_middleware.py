from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from py_backend_analytics.db.registry import get_db_client
from py_backend_analytics.extraction.extractors.fastapi_extractor import (
    FastAPIExtractor,
)
from py_backend_analytics.input_data import PyBackendAnalyticsInputData
from py_backend_analytics.models import RequestInfo


class PyBackendAnalyticsFastAPIMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, input_data: PyBackendAnalyticsInputData):
        super().__init__(app)
        self._initialized = False
        self._data = input_data
        self._logger = input_data.logger
        self._db_client = None

    async def dispatch(self, request: Request, call_next):
        try:
            if not self._initialized:
                await self._setup_db()
            request_info = FastAPIExtractor.extract(request)
            if self._should_save_request(request_info):
                await self._db_client.insert_request_info(request_info)
        except Exception as e:
            self._debug(
                f"Got an error when trying to extract info from the request: {e}"
            )
        return await call_next(request)

    async def _setup_db(self):
        self._db_client = await get_db_client(
            self._data.db_connection_string, self._data.db_type
        )

    def _debug(self, message: str):
        """Best effort to log"""
        if self._logger is not None:
            try:
                self._logger.debug(message)
            except Exception:
                pass

    def _should_save_request(self, request_info: RequestInfo):
        page = request_info.page
        return page not in self._data.excluded_endpoints and not any(
            page.startswith(fragment) for fragment in self._data.excluded_path_prefixes
        )
