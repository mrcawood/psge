"""Pytest fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_results_dir(tmp_path):
    """Temporary results directory for test runs."""
    d = tmp_path / "results"
    d.mkdir()
    return d
