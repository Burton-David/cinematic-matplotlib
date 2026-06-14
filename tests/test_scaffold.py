"""Tests for the editorial scaffolding helpers."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import cinestyle as cs


def test_finish_writes_title_and_subtitle_and_despines() -> None:
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [1, 3, 2])
    cs.finish(ax, "Revenue doubled", "Quarterly, USD", source="Source: filings")
    texts = [t.get_text() for t in ax.texts]
    assert "Revenue doubled" in texts
    assert "Quarterly, USD" in texts
    # The source line lives on the figure, not the axes.
    assert any("Source: filings" in t.get_text() for t in fig.texts)
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    plt.close(fig)


def test_thousands_formatter_inserts_separators() -> None:
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 12000])
    cs.thousands(ax, "y")
    fmt = ax.yaxis.get_major_formatter()
    assert fmt(12000, 0) == "12,000"
    plt.close(fig)


def test_currency_keeps_sign_before_symbol() -> None:
    fig, ax = plt.subplots()
    cs.currency(ax, "y", symbol="$")
    fmt = ax.yaxis.get_major_formatter()
    assert fmt(2500, 0) == "$2,500"
    assert fmt(-3000, 0) == "-$3,000"
    plt.close(fig)


def test_value_labels_label_every_bar() -> None:
    fig, ax = plt.subplots()
    ax.bar(["a", "b", "c"], [10, 20, 35])
    cs.value_labels(ax, "{:.0f}")
    labels = {t.get_text() for t in ax.texts}
    assert {"10", "20", "35"} <= labels
    plt.close(fig)


def test_lint_text_flags_em_and_en_dashes() -> None:
    fig, ax = plt.subplots()
    ax.set_title("Before — after")  # em dash
    ax.set_xlabel("2019–2024")  # en dash
    findings = cs.lint_text(fig)
    assert len(findings) == 2
    assert any("em dash" in f for f in findings)
    assert any("en dash" in f for f in findings)
    plt.close(fig)


def test_lint_text_clean_figure_returns_empty() -> None:
    fig, ax = plt.subplots()
    ax.set_title("All hyphens-are-fine here")
    assert cs.lint_text(fig) == []
    plt.close(fig)


def test_save_writes_at_300_dpi_and_makes_parents(tmp_path: object) -> None:
    from PIL import Image

    with cs.theme("margin_call"):
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot(np.arange(5))
        out = tmp_path / "nested" / "fig.png"  # type: ignore[operator]
        path = cs.save(fig, out)
    assert path.exists()
    with Image.open(path) as img:
        # 4 inches at 300 dpi is ~1200 px wide before the tight bbox trims margins.
        assert img.width > 900
        assert img.info.get("dpi", (0, 0))[0] >= 290
