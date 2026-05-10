from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_sqlite_engine(monkeypatch):
    def execute(query, params):
        pass

    mock_sql = MagicMock()
    mock_cursor = MagicMock()
    mock_sql.cursor = mock_cursor
    mock_cursor.execute = execute

    monkeypatch.setattr("sqlite3.connect", mock_sql)
