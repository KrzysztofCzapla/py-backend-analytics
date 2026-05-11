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
        self.db_client = get_db_client(
            input_data.db_connection_string, input_data.db_type
        )
        self.excluded_endpoints = input_data.excluded_endpoints
        self.excluded_path_prefixes = input_data.excluded_path_prefixes
        self.logger = input_data.logger

    async def dispatch(self, request: Request, call_next):
        try:
            request_info = FastAPIExtractor.extract(request)
            if self._should_save_request(request, request_info):
                self.db_client.insert_request_info(request_info)
        except Exception as e:
            self._debug(
                f"Got an error when trying to extract info from the request: {e}"
            )
        return await call_next(request)

    def _debug(self, message: str):
        """Best effort to log"""
        if self.logger is not None:
            try:
                self.logger.debug(message)
            except Exception:
                pass

    def _should_save_request(self, request: Request, request_info: RequestInfo):
        page = request_info.page
        return page not in self.excluded_endpoints and not any(
            page.startswith(fragment) for fragment in self.excluded_path_prefixes
        )
