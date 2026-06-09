"""Build epoch timeline reports from profile events (M1.3)."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.models.profile_event import ProfileEvent


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_timeline_report(run_id: str, events: list[ProfileEvent]) -> dict[str, Any]:
    by_epoch: dict[int, list[ProfileEvent]] = defaultdict(list)
    for ev in events:
        by_epoch[ev.epoch].append(ev)

    epochs: list[dict[str, Any]] = []
    for epoch in sorted(by_epoch.keys()):
        grouped: dict[str, list[ProfileEvent]] = defaultdict(list)
        for ev in by_epoch[epoch]:
            grouped[ev.phase].append(ev)

        phases: list[dict[str, Any]] = []
        max_duration = -1.0
        bottleneck: str | None = None

        for phase, rows in sorted(grouped.items()):
            total_ms = sum(r.duration_ms or 0 for r in rows)
            summary = {
                "phase": phase,
                "avg_cpu_percent": _avg([r.cpu_percent for r in rows if r.cpu_percent is not None]),
                "avg_gpu_percent": _avg([r.gpu_percent for r in rows if r.gpu_percent is not None]),
                "avg_throughput": _avg([r.throughput for r in rows if r.throughput is not None]),
                "total_duration_ms": total_ms if total_ms > 0 else None,
                "event_count": len(rows),
            }
            phases.append(summary)
            if total_ms > max_duration:
                max_duration = total_ms
                bottleneck = phase

        epochs.append({"epoch": epoch, "phases": phases, "bottleneck_phase": bottleneck})

    return {
        "run_id": run_id,
        "epochs": epochs,
        "total_events": len(events),
    }
