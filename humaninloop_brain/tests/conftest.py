"""Shared test fixtures and path helpers."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def load_fixture(fixtures_dir: Path):
    """Return a callable that loads a JSON fixture by name."""
    import json

    def _load(name: str) -> dict:
        path = fixtures_dir / name
        return json.loads(path.read_text())

    return _load
