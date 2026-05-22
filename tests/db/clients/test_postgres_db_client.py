from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from py_backend_analytics.db.constants import DBColumns, DB_TABLE_NAME
from py_backend_analytics.db.models import AnalyticsSummaryFields as F
from py_backend_analytics.models import RequestInfo


@pytest.mark.asyncio
async def test_insert_request_info(postgres_db_client, patched_connection):
    model = RequestInfo(
        location="PL",
        page="/home",
        source="google",
        datestamp=datetime.now(timezone.utc).isoformat(),
    )

    await postgres_db_client.insert_request_info(model)

    patched_connection.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_top_without_date(postgres_db_client, mock_conn):
    mock_conn.fetch.return_value = [
        ("PL", 10),
        (None, 3),
    ]

    result = await postgres_db_client._get_top(mock_conn, DBColumns.location)

    assert result == [
        {F.VALUE: "PL", F.COUNT: 10},
        {F.VALUE: "UNKNOWN", F.COUNT: 3},
    ]


@pytest.mark.asyncio
async def test_get_top_with_date_filter(postgres_db_client, mock_conn):
    mock_conn.fetch.return_value = []

    await postgres_db_client._get_top(
        mock_conn,
        DBColumns.location,
        min_date="2025-01-01",
    )

    query = mock_conn.fetch.await_args.args[0]
    params = mock_conn.fetch.await_args.args[1]

    assert "WHERE datestamp >= $1" in query
    assert params == "2025-01-01"


@pytest.mark.asyncio
async def test_db_table_exists_true(postgres_db_client, patched_connection):
    patched_connection.execute.return_value = (DB_TABLE_NAME,)

    result = await postgres_db_client._db_table_exists()

    assert result is True


@pytest.mark.asyncio
async def test_db_table_exists_false(postgres_db_client, patched_connection):
    patched_connection.fetchrow.return_value = None

    result = await postgres_db_client._db_table_exists()

    assert result is False


@pytest.mark.asyncio
async def test_create_db_table(postgres_db_client, patched_connection):
    await postgres_db_client._create_db_table()

    assert patched_connection.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_analytics_summary(postgres_db_client, patched_connection):
    patched_connection.fetch.return_value = [
        ("PL", "/home", "google", "2025-01-01T00:00:00+00:00")
    ]

    postgres_db_client._get_top = AsyncMock(
        side_effect=[
            [{"value": "PL", "count": 1}],
            [{"value": "/home", "count": 1}],
            [{"value": "google", "count": 1}],
        ]
        * 3
    )

    result = await postgres_db_client.get_analytics_summary()

    assert F.ALL_TIME in result
    assert F.LAST_MONTH in result
    assert F.LAST_YEAR in result
    assert F.RECENT_REQUESTS in result

    assert result[F.RECENT_REQUESTS][0][F.LOCATION] == "PL"
