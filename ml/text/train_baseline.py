"""train_baseline.py (text)

WHY THIS FILE EXISTS
    Trains and honestly benchmarks the traditional-ML candidates for the
    structured symptom -> disease predictor: Logistic Regression (the
    interpretability baseline), Random Forest, and XGBoost (the
    candidate favored in PHASE1_RESEARCH.md, to be proven here rather
    than assumed). This is Phase 4 of the plan -- Phase 5 adds an MLP
    for comparison, Phase 6 picks the final model based on what both
    phases actually measure.

INPUT
    data/processed/text/candidate_a_structured/{train,val,test}.csv
    (produced by ml/text/prepare_dataset.py). Binary symptom columns +
    one disease label column.

    If that directory doesn't exist yet (Candidate A not downloaded from
    Kaggle), pass --data-dir to point at any directory with the same
    train/val/test.csv shape -- this is how the pipeline can be smoke-
    tested against the Candidate B mirror before Candidate A is available.
    Results from a --data-dir other than candidate_a_structured are
    NEVER written to docs/MODEL_CARD.md as if they were the real
    benchmark -- see the "smoke_test" flag in the output manifest.

OUTPUT
    artifacts/text_model/candidates/{logreg,random_forest,xgboost}/
        model.joblib
        val_metrics.json, test_metrics.json  (from ml/common/metrics.py)
    artifacts/text_model/experiments/*.json  (from ml/common/reproducibility.py)
    Printed comparison table across all three models.

HOW TO RUN
    python ml/text/train_baseline.py
    python ml/text/train_baseline.py --data-dir data/processed/text/candidate_b_smoketest --smoke-test

HOW IT CONNECTS
    ml/text/prepare_dataset.py -> THIS FILE -> ml/text/evaluate.py
    (re-evaluation/reporting) -> Phase 6 model-selection decision,
    recorded in docs/MODEL_CARD.md. backend/inference/predictor.py loads
    whichever artifact Phase 6 selects -- it does not import this file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ml.common.metrics import evaluate_classification  # noqa: E402
from ml.common.reproducibility import Timer, log_experiment, set_seed  # noqa: E402

DEFAULT_DATA_DIR = REPO_ROOT / "data" / "processed" / "text" / "candidate_a_structured"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "text_model"


def load_split(data_dir: Path, name: str) -> pd.DataFrame:
    path = data_dir / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run ml/text/prepare_dataset.py first, or pass "
            "--data-dir pointing at a directory with train/val/test.csv."
        )
    return pd.read_csv(path)


def xy_split(df: pd.DataFrame, label_encoder: LabelEncoder, label_col: str):
    X = df.drop(columns=[label_col]).values
    y = label_encoder.transform(df[label_col].values)
    return X, y


def build_models(seed: int) -> dict:
    models = {
        "logreg": LogisticRegression(
            max_iter=1000, random_state=seed
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=None, class_weight="balanced_subsample",
            random_state=seed, n_jobs=-1,
        ),
    }
    try:
        from xgboost import XGBClassifier
        models["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.1,
            objective="multi:softprob", eval_metric="mlogloss",
            random_state=seed, n_jobs=-1,
        )
    except ImportError:
        print("xgboost not installed -- skipping XGBoost candidate. "
              "Install with: pip install xgboost --break-system-packages")
    return models


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="Mark this run's manifests as a pipeline smoke test, not a real "
             "benchmark result, so it's never mistaken for the Phase 6 decision data.",
    )
    args = parser.parse_args()
    args.data_dir = args.data_dir.resolve()
    set_seed(args.seed)

    label_col_candidates = ["prognosis", "disease", "Disease"]
    train_df = load_split(args.data_dir, "train")
    val_df = load_split(args.data_dir, "val")
    test_df = load_split(args.data_dir, "test")

    label_col = next((c for c in label_col_candidates if c in train_df.columns), train_df.columns[-1])

    le = LabelEncoder()
    le.fit(pd.concat([train_df[label_col], val_df[label_col], test_df[label_col]]))

    X_train, y_train = xy_split(train_df, le, label_col)
    X_val, y_val = xy_split(val_df, le, label_col)
    X_test, y_test = xy_split(test_df, le, label_col)

    class_names = list(le.classes_)
    dataset_version = str(args.data_dir.relative_to(REPO_ROOT))

    models = build_models(args.seed)
    results_summary = []

    for name, model in models.items():
        print(f"\n=== Training {name} ===")
        with Timer() as t:
            model.fit(X_train, y_train)

        val_pred = model.predict(X_val)
        val_proba = model.predict_proba(X_val) if hasattr(model, "predict_proba") else None
        val_report = evaluate_classification(y_val, val_pred, val_proba, class_names)

        test_pred = model.predict(X_test)
        test_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        test_report = evaluate_classification(y_test, test_pred, test_proba, class_names)

        model_dir = ARTIFACTS_DIR / "candidates" / name
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": model, "label_encoder": le, "feature_columns": list(
            train_df.drop(columns=[label_col]).columns)}, model_dir / "model.joblib")
        val_report.save(model_dir / "val_metrics.json")
        test_report.save(model_dir / "test_metrics.json")

        manifest_path = log_experiment(
            artifacts_dir=ARTIFACTS_DIR,
            experiment_name=f"{'smoketest_' if args.smoke_test else ''}{name}",
            model_type=name,
            dataset_version=dataset_version,
            seed=args.seed,
            hyperparameters=model.get_params(),
            training_time_seconds=t.elapsed,
            val_metrics={"accuracy": val_report.accuracy, "f1_macro": val_report.f1_macro},
            test_metrics={"accuracy": test_report.accuracy, "f1_macro": test_report.f1_macro},
            notes=(
                "SMOKE TEST ONLY -- not a real benchmark result, run against "
                f"{dataset_version}, not the Candidate A backbone."
                if args.smoke_test else ""
            ),
        )

        print(f"  val  accuracy={val_report.accuracy:.4f}  f1_macro={val_report.f1_macro:.4f}")
        print(f"  test accuracy={test_report.accuracy:.4f}  f1_macro={test_report.f1_macro:.4f}")
        if test_report.warnings:
            for w in test_report.warnings:
                print(f"  [WARNING] {w}")
        print(f"  manifest: {manifest_path.relative_to(REPO_ROOT)}")

        results_summary.append({
            "model": name,
            "val_accuracy": val_report.accuracy,
            "val_f1_macro": val_report.f1_macro,
            "test_accuracy": test_report.accuracy,
            "test_f1_macro": test_report.f1_macro,
            "training_time_s": round(t.elapsed, 2),
            "warnings": test_report.warnings,
        })

    print("\n=== Comparison (test set) ===")
    print(f"{'model':<15}{'accuracy':<12}{'f1_macro':<12}{'train_time_s':<15}{'warnings'}")
    for r in results_summary:
        flag = "  <-- SEE WARNING" if r["warnings"] else ""
        print(f"{r['model']:<15}{r['test_accuracy']:<12.4f}{r['test_f1_macro']:<12.4f}"
              f"{r['training_time_s']:<15}{flag}")

    summary_path = ARTIFACTS_DIR / "candidates" / (
        "smoketest_comparison.json" if args.smoke_test else "baseline_comparison.json"
    )
    with open(summary_path, "w") as f:
        json.dump({"data_dir": dataset_version, "smoke_test": args.smoke_test,
                    "results": results_summary}, f, indent=2)
    print(f"\nComparison saved to {summary_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
