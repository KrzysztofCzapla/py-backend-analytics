from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from py_backend_analytics.db.registry import DB_CLIENTS
from py_backend_analytics.extraction.extractors.fastapi_extractor import (
    FastAPIExtractor,
)
from py_backend_analytics.input_data import PyBackendAnalyticsInputData


class MyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, input_data: PyBackendAnalyticsInputData):
        super().__init__(app)
        db_client_class = DB_CLIENTS.get(input_data.db_type)
        if not db_client_class:
            raise ValueError(f"Provided wrong DB type: {input_data.db_type}")
        self.db_client = db_client_class(input_data.db_connection_string)
        self.excluded_endpoints = input_data.excluded_endpoints
        self.logger = input_data.logger

    def debug(self, message: str):
        """Best effort to log"""
        if self.logger is not None:
            try:
                self.logger.debug(message)
            except Exception:
                pass

    async def dispatch(self, request: Request, call_next):
        try:
            request_info = FastAPIExtractor.extract(request)
            if request_info.page not in self.excluded_endpoints:
                self.db_client.insert_request_info(request_info)
        except Exception as e:
            self.debug(
                f"Got an error when trying to extract info from the request: {e}"
            )
        return await call_next(request)
