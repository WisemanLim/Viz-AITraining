"""SVG export for neural architecture diagrams (M2.2)."""
from __future__ import annotations

import html
from typing import Any

LAYER_GAP = 200
NODE_GAP = 52
NODE_R = 14


def _node_fill(hue: str, activation: float) -> str:
    alpha = 0.5 + activation * 0.5
    if hue == "input":
        return f"rgba(56,189,248,{alpha:.2f})"
    if hue == "output":
        return f"rgba(192,132,252,{alpha:.2f})"
    return f"rgba(251,146,60,{alpha:.2f})"


def architecture_to_svg(arch: dict[str, Any]) -> str:
    layers = arch["layers"]
    edges = arch.get("edges", [])
    formulas = arch.get("formulas", [])

    positions: dict[str, tuple[float, float]] = {}
    for li, layer in enumerate(layers):
        x = 80 + li * LAYER_GAP
        nodes = layer["nodes"]
        total_h = (len(nodes) - 1) * NODE_GAP
        for ni, node in enumerate(nodes):
            positions[node["id"]] = (x, 80 + ni * NODE_GAP - total_h / 2 + 120)

    width = 80 + len(layers) * LAYER_GAP + 80
    max_nodes = max((len(l["nodes"]) for l in layers), default=1)
    height = max_nodes * NODE_GAP + 200

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#0f172a"/>',
        '<defs><filter id="glow"><feGaussianBlur stdDeviation="3"/>'
        "<feMerge><feMergeNode/><feMergeNode in=\"SourceGraphic\"/></feMerge></filter></defs>",
    ]

    for f in formulas:
        parts.append(
            f'<text x="{f["x"] * width:.1f}" y="{f["y"] * height:.1f}" '
            f'fill="#64748b" font-size="11" font-family="monospace" opacity="0.7">'
            f"{html.escape(f['text'])}</text>"
        )

    for edge in edges:
        s = positions.get(edge["source"])
        t = positions.get(edge["target"])
        if not s or not t:
            continue
        mx, my = (s[0] + t[0]) / 2, (s[1] + t[1]) / 2
        w = edge.get("weight", 0)
        stroke = "#22d3ee" if w >= 0 else "#f87171"
        parts.append(
            f'<line x1="{s[0] + NODE_R}" y1="{s[1]}" x2="{t[0] - NODE_R}" y2="{t[1]}" '
            f'stroke="{stroke}" stroke-width="1" opacity="0.35"/>'
        )
        parts.append(
            f'<text x="{mx}" y="{my - 4}" fill="#94a3b8" font-size="8" '
            f'text-anchor="middle" font-family="monospace">{html.escape(edge.get("label", ""))}</text>'
        )

    for layer in layers:
        if not layer["nodes"]:
            continue
        lx = positions[layer["nodes"][0]["id"]][0]
        name = html.escape(layer["name"])
        size = layer.get("size", len(layer["nodes"]))
        parts.append(
            f'<text x="{lx}" y="30" fill="#94a3b8" font-size="11" '
            f'text-anchor="middle" font-weight="600">{name} ({size})</text>'
        )
        if layer.get("kind") == "hidden":
            bias = html.escape(layer.get("bias", {}).get("label", ""))
            parts.append(
                f'<text x="{lx + 60}" y="24" fill="#fbbf24" font-size="9" '
                f'font-family="monospace">BIAS {bias}</text>'
            )
        for node in layer["nodes"]:
            p = positions.get(node["id"])
            if not p:
                continue
            fill = _node_fill(node["hue"], node["activation"])
            parts.append(
                f'<circle cx="{p[0]}" cy="{p[1]}" r="{NODE_R}" fill="{fill}" '
                f'stroke="#e2e8f0" stroke-width="1.5" filter="url(#glow)"/>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def svg_to_png(svg: str) -> bytes:
    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError("PNG export requires cairosvg") from exc
    return cairosvg.svg2png(bytestring=svg.encode("utf-8"))


def svg_to_pdf(svg: str) -> bytes:
    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError("PDF export requires cairosvg") from exc
    return cairosvg.svg2pdf(bytestring=svg.encode("utf-8"))
