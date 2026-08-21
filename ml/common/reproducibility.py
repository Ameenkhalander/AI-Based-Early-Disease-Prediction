"""reproducibility.py

WHY THIS FILE EXISTS
    Sets random seeds consistently across libraries and writes a JSON
    "experiment manifest" for every training run -- dataset version,
    seed, model architecture, hyperparameters, training time, and
    val/test metrics -- per the project's experiment-tracking
    requirement. Kept as a lightweight JSON file per run rather than
    requiring MLflow infrastructure up front; MLflow can be layered on
    later without changing what gets recorded, just where it's stored.

INPUT
    set_seed(seed): called once at the top of every train_*.py script.
    log_experiment(...): called once at the end of every train_*.py
    script, after evaluation.

OUTPUT
    artifacts/<model>/experiments/<timestamp>_<name>.json manifest files.

HOW IT CONNECTS
    ml/text/train_baseline.py, train_deep_learning.py, and the eventual
    ml/vision/* scripts both call this at the start and end of a run.
"""

from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def set_seed(seed: int) -> None:
    """Seed every RNG this project's training code touches.
    Only imports torch if it's actually installed, so this stays usable
    in the sklearn-only baseline scripts without a torch dependency.
    """
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch  # noqa: WPS433 (intentional local import)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


@dataclass
class ExperimentManifest:
    experiment_name: str
    model_type: str
    dataset_version: str  # e.g. path/hash of the data_card.json used
    seed: int
    hyperparameters: dict
    training_time_seconds: float
    val_metrics: dict = field(default_factory=dict)
    test_metrics: dict = field(default_factory=dict)
    notes: str = ""
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Timer:
    """Small context manager for training_time_seconds.

    Usage:
        with Timer() as t:
            model.fit(X, y)
        manifest = log_experiment(..., training_time_seconds=t.elapsed)
    """

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.time() - self._start


def log_experiment(
    artifacts_dir: Path,
    experiment_name: str,
    model_type: str,
    dataset_version: str,
    seed: int,
    hyperparameters: dict,
    training_time_seconds: float,
    val_metrics: dict | None = None,
    test_metrics: dict | None = None,
    notes: str = "",
) -> Path:
    manifest = ExperimentManifest(
        experiment_name=experiment_name,
        model_type=model_type,
        dataset_version=dataset_version,
        seed=seed,
        hyperparameters=hyperparameters,
        training_time_seconds=training_time_seconds,
        val_metrics=val_metrics or {},
        test_metrics=test_metrics or {},
        notes=notes,
    )
    out_dir = Path(artifacts_dir) / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = manifest.timestamp_utc.replace(":", "-")
    out_path = out_dir / f"{ts}_{experiment_name}.json"
    with open(out_path, "w") as f:
        json.dump(asdict(manifest), f, indent=2)
    return out_path
