import pytest

import app.main as main_module


@pytest.fixture(autouse=True)
def disable_database_lifecycle(monkeypatch):
    """
    Prevent tests from opening or closing the real
    PostgreSQL connection pool during application startup.
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
