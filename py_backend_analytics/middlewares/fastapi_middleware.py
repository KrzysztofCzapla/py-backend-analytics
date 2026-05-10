from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from py_backend_analytics.db.registry import DB_CLIENTS
from py_backend_analytics.enums import PyBackendAnalyticsDB
from py_backend_analytics.extraction.fastapi_extractor import FastAPIExtractor


class MyMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        db_connection_string: str,
        db: PyBackendAnalyticsDB = PyBackendAnalyticsDB.SQLITE,
    ):
        super().__init__(app)
        db_client_class = DB_CLIENTS.get(db)
        if not db_client_class:
            raise ValueError(f"Provided wrong DB type: {db}")
        self.db_client = db_client_class(db_connection_string)

    async def dispatch(self, request: Request, call_next):
        request_info = FastAPIExtractor.extract(request)
        self.db_client.insert_request_info(request_info)
        return await call_next(request)
