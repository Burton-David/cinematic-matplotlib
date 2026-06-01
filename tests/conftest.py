"""Shared test fixtures: headless backend and per-test rcParams isolation."""

from __future__ import annotations

from collections.abc import Iterator

import matplotlib

matplotlib.use("Agg")

import matplotlib as mpl  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolate_rcparams() -> Iterator[None]:
    """Snapshot rcParams before each test and restore them afterwards.

    Styles mutate global state by design (``apply``, ``plt.style.use``), so
    isolating each test keeps one test's styling from bleeding into the next.
    """
    snapshot = mpl.rcParams.copy()
    try:
        yield
    finally:
        mpl.rcParams.update(snapshot)
        plt.close("all")
