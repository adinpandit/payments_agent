import pytest

import app.main as main_module


@pytest.fixture(autouse=True)
def disable_database_lifecycle(monkeypatch):
    """
    Prevent ordinary API tests from opening
    the real PostgreSQL connection pool.
    """

    monkeypatch.setattr(
        main_module,
        "open_pool",
        lambda: None,
    )

    monkeypatch.setattr(
        main_module,
        "close_pool",
        lambda: None,
    )
