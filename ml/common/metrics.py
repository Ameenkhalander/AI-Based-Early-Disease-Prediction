"""metrics.py

WHY THIS FILE EXISTS
    Shared evaluation utilities used by BOTH ml/text and ml/vision, so
    every model in this project is judged the same way. Centralizing
    this avoids subtly different metric definitions between the text
    and vision training scripts (e.g. one script using macro-F1 and
    another quietly using weighted-F1, which are not comparable).

INPUT
    y_true, y_pred: array-like of class labels
    y_proba: optional array-like of predicted class probabilities
             (n_samples, n_classes), enables ROC-AUC and calibration.
    class_names: optional list[str] for a readable per-class report.

OUTPUT
    A single EvaluationReport dataclass containing everything
    docs/MODEL_CARD.md needs: accuracy, macro/weighted precision-recall-F1,
    per-class F1, the confusion matrix, and (if y_proba given) macro
    ROC-AUC.

HOW IT CONNECTS
    ml/text/train_baseline.py, train_deep_learning.py, evaluate.py, and
    the eventual ml/vision/* training scripts all import from here rather
    than reimplementing sklearn.metrics calls independently.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationReport:
    accuracy: float
    balanced_accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    per_class_report: dict
    confusion_matrix: list  # list[list[int]], JSON-serializable
    class_labels: list
    roc_auc_macro_ovr: float | None = None
    n_test_samples: int = 0
    warnings: list = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)


def evaluate_classification(
    y_true,
    y_pred,
    y_proba: np.ndarray | None = None,
    class_names: list[str] | None = None,
) -> EvaluationReport:
    """Compute the full standard metric set for one trained model.

    DESIGN NOTE: this function NEVER decides pass/fail or "good enough" --
    it only measures. Interpretation (e.g. "is 100% accuracy suspicious
    given this dataset's known leakage") belongs in the calling script
    and in docs/MODEL_CARD.md, not hard-coded here.
    """
    labels = sorted(set(list(y_true) + list(y_pred)))
    warnings: list[str] = []

    report_dict = classification_report(
        y_true, y_pred, labels=labels, target_names=class_names,
        output_dict=True, zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    roc_auc = None
    if y_proba is not None:
        try:
            roc_auc = float(
                roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro", labels=labels)
            )
        except ValueError as e:
            warnings.append(f"ROC-AUC could not be computed: {e}")

    acc = float(accuracy_score(y_true, y_pred))
    if acc > 0.98:
        warnings.append(
            "Accuracy > 98%. Do NOT report this as a success without investigating "
            "data leakage (duplicate/near-duplicate rows, train/test overlap) -- "
            "see ml/text/prepare_dataset.py's duplicate checks."
        )

    return EvaluationReport(
        accuracy=acc,
        balanced_accuracy=float(balanced_accuracy_score(y_true, y_pred)),
        precision_macro=float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        recall_macro=float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        f1_macro=float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        precision_weighted=float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        recall_weighted=float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        f1_weighted=float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        per_class_report=report_dict,
        confusion_matrix=cm.tolist(),
        class_labels=[str(l) for l in labels],
        roc_auc_macro_ovr=roc_auc,
        n_test_samples=len(y_true),
        warnings=warnings,
    )
