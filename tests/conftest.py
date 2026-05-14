from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from py_backend_analytics.db.clients.sqlite_db_client import SQLiteDBClient
from py_backend_analytics.enums import PyBackendAnalyticsDB
from py_backend_analytics.input_data import PyBackendAnalyticsInputData
from py_backend_analytics.middlewares.fastapi_middleware import (
    PyBackendAnalyticsFastAPIMiddleware,
)


@pytest.fixture
def db_client():
    client = SQLiteDBClient(connection_string=":memory:")
    return client


@pytest.fixture
def mock_conn():
    conn = AsyncMock()

    conn.cursor.return_value = AsyncMock()
    conn.execute.return_value.fetchall.return_value = []
    conn.execute.return_value.fetchone.return_value = None

    return conn


@pytest.fixture
def patched_connection(db_client, mock_conn):
    @asynccontextmanager
    async def _mocked():
        yield mock_conn

    db_client._get_connection = MagicMock(return_value=_mocked())

    return mock_conn


@pytest.fixture()
def completely_mocked_db(monkeypatch):
    db_mock = AsyncMock()
    db_mock.create.return_value = db_mock

    monkeypatch.setattr(
        "py_backend_analytics.db.registry.DB_CLIENTS",
        {PyBackendAnalyticsDB.SQLITE: db_mock},
    )

    return db_mock


@pytest.fixture(autouse=True)
def ip_country_lookup(monkeypatch):
    class FakeDB:
        def get(self, ip):
            if ip == "1.1.1.1":
                return {"country": {"names": {"en": "Australia"}}}

    monkeypatch.setattr(
        "py_backend_analytics.extraction.geo_lookup.maxminddb.open_database",
        lambda _: FakeDB(),
    )

    monkeypatch.setattr(
        "py_backend_analytics.extraction.geo_lookup.Path.exists",
        lambda *_: True,
    )


@pytest.fixture()
def test_client(completely_mocked_db):
    app = FastAPI()
    db_string = "mydb.db"
    input_data = PyBackendAnalyticsInputData(db_string)
    app.add_middleware(PyBackendAnalyticsFastAPIMiddleware, input_data)

    @app.get("/my-endpoint")
    async def my_endpoint():
        return {"msg": "my_message"}

    return TestClient(app)
