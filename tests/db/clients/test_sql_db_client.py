from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from py_backend_analytics.db.constants import DBColumns, DB_TABLE_NAME
from py_backend_analytics.db.models import AnalyticsSummaryFields as F
from py_backend_analytics.models import RequestInfo


@pytest.mark.asyncio
async def test_insert_request_info(db_client, patched_connection):
    model = RequestInfo(
        location="PL",
        page="/home",
        source="google",
        datestamp=datetime.now(timezone.utc).isoformat(),
    )

    await db_client.insert_request_info(model)

    cursor = patched_connection.cursor.return_value

    cursor.execute.assert_awaited_once()
    patched_connection.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_top_without_date(db_client, mock_conn):
    mock_conn.execute.return_value.fetchall.return_value = [
        ("PL", 10),
        (None, 3),
    ]

    result = await db_client._get_top(mock_conn, DBColumns.location)

    assert result == [
        {F.VALUE: "PL", F.COUNT: 10},
        {F.VALUE: "UNKNOWN", F.COUNT: 3},
    ]


@pytest.mark.asyncio
async def test_get_top_with_date_filter(db_client, mock_conn):
    mock_conn.execute.return_value.fetchall.return_value = []

    await db_client._get_top(
        mock_conn,
        DBColumns.location,
        min_date="2025-01-01",
    )

    query = mock_conn.execute.await_args.args[0]
    params = mock_conn.execute.await_args.args[1]

    assert "WHERE datestamp >= ?" in query
    assert params == ["2025-01-01"]


@pytest.mark.asyncio
async def test_db_table_exists_true(db_client, patched_connection):
    patched_connection.cursor.return_value.execute.return_value.fetchone.return_value = (
        DB_TABLE_NAME,
    )

    result = await db_client._db_table_exists()

    assert result is True


@pytest.mark.asyncio
async def test_db_table_exists_false(db_client, patched_connection):
    patched_connection.cursor.return_value.execute.return_value.fetchone.return_value = None

    result = await db_client._db_table_exists()

    assert result is False


@pytest.mark.asyncio
async def test_create_db_table(db_client, patched_connection):
    await db_client._create_db_table()

    cursor = patched_connection.cursor.return_value

    assert cursor.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_analytics_summary(db_client, patched_connection):
    patched_connection.execute.return_value.fetchall.return_value = [
        ("PL", "/home", "google", "2025-01-01T00:00:00+00:00")
    ]

    db_client._get_top = AsyncMock(
        side_effect=[
            [{"value": "PL", "count": 1}],
            [{"value": "/home", "count": 1}],
            [{"value": "google", "count": 1}],
        ]
        * 3
    )

    result = await db_client.get_analytics_summary()

    assert F.ALL_TIME in result
    assert F.LAST_MONTH in result
    assert F.LAST_YEAR in result
    assert F.RECENT_REQUESTS in result

    assert result[F.RECENT_REQUESTS][0][F.LOCATION] == "PL"
