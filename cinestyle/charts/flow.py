"""Sankey flow diagram.

A flow diagram routes quantities between nodes, with ribbon width proportional
to value. The renderer here is pure matplotlib (Bezier ribbons and node bars), so
the core install carries it; the ``[flow]`` extra only adds pandas for the
convenience of passing a tidy ``source, target, value`` frame.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from matplotlib.axes import Axes
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from . import _base

Link = tuple[str, str, float]


def _as_links(data: Any) -> list[Link]:
    """Accept a list of triples or a tidy frame with source/target/value columns."""
    if hasattr(data, "itertuples"):  # a pandas DataFrame, without importing pandas
        cols = {c.lower(): c for c in data.columns}
        s, t, v = cols["source"], cols["target"], cols["value"]
        return [(str(r[s]), str(r[t]), float(r[v])) for _, r in data.iterrows()]
    return [(str(s), str(t), float(v)) for s, t, v in data]


def _layer_nodes(links: list[Link]) -> tuple[list[str], dict[str, int]]:
    """Order the nodes and assign each a layer by longest path from a source."""
    nodes: list[str] = list(
        dict.fromkeys([n for link in links for n in (link[0], link[1])])
    )
    layer = dict.fromkeys(nodes, 0)
    # Relax layers V times; this settles longest paths and tolerates a stray
    # back-edge (it just stops moving) rather than recursing into a cycle.
    for _ in range(len(nodes)):
        changed = False
        for src, dst, _value in links:
            if layer[dst] < layer[src] + 1:
                layer[dst] = layer[src] + 1
                changed = True
        if not changed:
            break
    return nodes, layer


def _ribbon(x0: float, y0: float, x1: float, y1: float, thickness: float) -> Path:
    """A filled cubic Bezier ribbon from the right edge of one node to another."""
    mid = (x0 + x1) / 2
    half = thickness / 2
    verts = [
        (x0, y0 + half),
        (mid, y0 + half),
        (mid, y1 + half),
        (x1, y1 + half),
        (x1, y1 - half),
        (mid, y1 - half),
        (mid, y0 - half),
        (x0, y0 - half),
        (x0, y0 + half),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.LINETO,
        Path.CURVE4,
        Path.CURVE4,
        Path.CURVE4,
        Path.CLOSEPOLY,
    ]
    return Path(verts, codes)


def sankey(
    data: Any,
    ax: Axes | None = None,
    *,
    node_width: float = 0.04,
    gap: float = 0.02,
    ribbon_alpha: float = 0.55,
    labels: bool = True,
) -> Axes:
    """Draw a Sankey flow diagram from ``source, target, value`` links.

    Nodes are placed in columns by longest path from a source, sized by the
    larger of their inflow and outflow, and connected by Bezier ribbons whose
    width is the flow value. Each ribbon takes its source node's color, so a
    quantity keeps its identity as it splits and merges downstream.

    Args:
        data: An iterable of ``(source, target, value)`` triples, or a pandas
            frame with those columns (any case).
        ax: Target axes (defaults to the current axes).
        node_width: Node bar width, in the normalized [0, 1] drawing space.
        gap: Vertical gap between stacked nodes in a column, same units.
        ribbon_alpha: Opacity of the flow ribbons.
        labels: Annotate each node with its name.

    Returns:
        The axes.
    """
    ax = _base.current_ax(ax)
    links = _as_links(data)
    nodes, layer = _layer_nodes(links)
    node_color = {n: _base.nth(i) for i, n in enumerate(nodes)}

    inflow: dict[str, float] = defaultdict(float)
    outflow: dict[str, float] = defaultdict(float)
    for src, dst, value in links:
        outflow[src] += value
        inflow[dst] += value
    throughput = {n: max(inflow[n], outflow[n]) for n in nodes}

    columns: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        columns[layer[node]].append(node)
    n_layers = max(layer.values()) + 1

    # Scale heights so the busiest column fills the canvas minus its gaps.
    scale = 1.0
    for members in columns.values():
        total = sum(throughput[n] for n in members) + gap * (len(members) - 1)
        if total > 0:
            scale = min(scale, 1.0 / total)

    node_x: dict[str, float] = {}
    node_top: dict[str, float] = {}
    for depth, members in columns.items():
        x = depth / max(n_layers - 1, 1) * (1 - node_width)
        stacked = sum(throughput[n] for n in members) * scale + gap * (len(members) - 1)
        cursor = 0.5 + stacked / 2  # center the column vertically, fill downward
        for node in members:
            height = throughput[node] * scale
            node_x[node] = x
            node_top[node] = cursor
            ax.add_patch(
                _rect(x, cursor - height, node_width, height, node_color[node])
            )
            if labels:
                ax.annotate(
                    node,
                    (x + node_width + 0.01, cursor - height / 2),
                    ha="left",
                    va="center",
                    color=_base.foreground(),
                    fontsize=9,
                )
            cursor -= height + gap

    out_cursor = {n: node_top[n] for n in nodes}
    in_cursor = {n: node_top[n] for n in nodes}
    for src, dst, value in links:
        thickness = value * scale
        y0 = out_cursor[src] - thickness / 2
        y1 = in_cursor[dst] - thickness / 2
        path = _ribbon(node_x[src] + node_width, y0, node_x[dst], y1, thickness)
        ax.add_patch(
            PathPatch(
                path, facecolor=node_color[src], edgecolor="none", alpha=ribbon_alpha
            )
        )
        out_cursor[src] -= thickness
        in_cursor[dst] -= thickness

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.axis("off")
    return ax


def _rect(x: float, y: float, width: float, height: float, color: str) -> PathPatch:
    verts = [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), facecolor=color, edgecolor="none")
