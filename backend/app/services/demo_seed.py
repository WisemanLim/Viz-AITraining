"""Seed a demo experiment with sample metrics for local onboarding."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.classical_chart import ClassicalChart
from app.models.internal_metric import InternalMetric
from app.models.profile_event import ProfileEvent
from app.models.run import Run
from app.models.scalar_metric import ScalarMetric
from app.models.xai_attribution import XaiAttribution


def seed_demo_run(db: Session, *, name: str = "demo-experiment") -> dict[str, Any]:
    """Create one run with representative scalars, profile, classical, internal, XAI."""
    run = Run(
        name=name,
        status="completed",
        params_json=json.dumps({"lr": 0.001, "epochs": 5, "demo": True}),
    )
    db.add(run)
    db.flush()

    scalars = [
        ScalarMetric(run_id=run.id, tag="loss", value=0.92, step=0),
        ScalarMetric(run_id=run.id, tag="loss", value=0.61, step=50),
        ScalarMetric(run_id=run.id, tag="loss", value=0.38, step=100),
        ScalarMetric(run_id=run.id, tag="accuracy", value=0.55, step=0),
        ScalarMetric(run_id=run.id, tag="accuracy", value=0.78, step=50),
        ScalarMetric(run_id=run.id, tag="accuracy", value=0.89, step=100),
    ]
    db.add_all(scalars)

    db.add(
        ProfileEvent(
            run_id=run.id,
            epoch=1,
            phase="train",
            cpu_percent=0.42,
            gpu_percent=0.71,
            throughput=1280.0,
            step=50,
        )
    )

    db.add(
        ClassicalChart(
            run_id=run.id,
            chart_type="learning_curve",
            title="Demo learning curve",
            data_json=json.dumps(
                {
                    "train_sizes": [100, 500, 1000],
                    "train_scores": [0.72, 0.81, 0.87],
                    "val_scores": [0.68, 0.76, 0.84],
                }
            ),
        )
    )

    db.add(
        InternalMetric(
            run_id=run.id,
            kind="activation_map",
            layer="hidden",
            step=100,
            title="Demo activation",
            data_json=json.dumps(
                {
                    "width": 2,
                    "height": 2,
                    "values": [[0.2, 0.8], [0.5, 0.3]],
                }
            ),
        )
    )

    db.add(
        XaiAttribution(
            run_id=run.id,
            method="shap",
            scope="temporal",
            title="Demo temporal SHAP",
            data_json=json.dumps(
                {
                    "steps": [0, 50, 100],
                    "features": ["age", "score"],
                    "values_over_time": [[0.1, 0.2], [0.15, 0.18], [0.22, 0.09]],
                }
            ),
        )
    )

    db.commit()
    db.refresh(run)

    return {
        "run_id": run.id,
        "name": run.name,
        "scalars": len(scalars),
        "message": "Demo run created. Refresh the dashboard.",
    }
