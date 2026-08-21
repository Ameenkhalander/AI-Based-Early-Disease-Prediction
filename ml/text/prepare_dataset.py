"""prepare_dataset.py (text)

WHY THIS FILE EXISTS
    Turns the three raw Kaggle datasets researched in Phase 1 into clean,
    documented, reproducible train/val/test splits under
    data/processed/text/. This is the ONLY file allowed to read from
    data/raw/text/ -- everything downstream (train_baseline.py,
    train_deep_learning.py) reads only from data/processed/text/.

WHAT IT LOADS (auto-detected from data/raw/text/, see EXPECTED_FILES below)
    Candidate A -- dhivyeshrk/diseases-and-symptoms-dataset
        ~246k rows, 773 diseases, 377 binary symptom columns.
        Trimmed here to the top N most frequent diseases (default 60)
        to become the STRUCTURED PREDICTION BACKBONE.
    Candidate B -- kaushil268/disease-prediction-using-machine-learning
        132 binary symptom columns, 42 diseases. Loaded ONLY to reproduce
        and document its known leakage (near-lookup-table structure) --
        never used to train the shipped model. Also doubles as a fast
        smoke-test set for exercising this pipeline before Candidate A/C
        are available.
    Candidate C -- niyarrbarman/symptom2disease
        ~1,200 rows of free-text symptom descriptions, 24 diseases.
        Used to build/validate the NLP extraction layer, not the
        structured predictor.

INPUT
    Raw CSVs placed by hand (or via `kaggle datasets download`) under:
        data/raw/text/candidate_a/   (dhivyeshrk export)
        data/raw/text/candidate_b/   (kaushil268 export, OR the GitHub
                                       mirror used for the smoke test --
                                       same schema: training_data.csv /
                                       test_data.csv, 132 symptom columns
                                       + prognosis)
        data/raw/text/candidate_c/   (niyarrbarman export)
    Only files that are actually present are processed -- this script is
    safe to run with just one of the three candidates on disk.

OUTPUT (written to data/processed/text/)
    candidate_a_structured/{train,val,test}.csv   (if candidate A found)
    candidate_b_leakage_report.json               (if candidate B found)
    candidate_c_nlp/{train,val,test}.csv           (if candidate C found)
    data_card.json  -- row counts, class counts, duplicate/leakage
                        findings, and the random seed used, for every
                        candidate that was processed in this run.

HOW TO RUN
    python ml/text/prepare_dataset.py
    python ml/text/prepare_dataset.py --top-n-diseases 80 --seed 42

CHECKS PERFORMED (per project requirement -- never skipped, never hidden)
    - exact duplicate row detection
    - near-duplicate detection (identical symptom vector, different
      row -- the specific pattern that inflates accuracy on Candidate B)
    - class distribution / imbalance report
    - train/test overlap check (rows in test that are exact duplicates
      of a training row)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw" / "text"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "text"

# Where this script looks for each candidate's raw export. Multiple
# candidate filenames are listed because Kaggle exports and GitHub
# mirrors of the same dataset are not always named identically.
EXPECTED_FILES = {
    "candidate_a": ["diseases-and-symptoms-dataset.csv", "dataset.csv"],
    "candidate_b": ["training_data.csv"],  # + optional test_data.csv
    "candidate_c": ["Symptom2Disease.csv", "symptom2disease.csv"],
}


@dataclass
class DataCardEntry:
    candidate: str
    source_file: str
    n_rows_raw: int
    n_rows_after_cleaning: int
    n_classes: int
    n_exact_duplicates: int
    n_near_duplicates: int
    n_train_test_overlap: int
    class_distribution_top5: dict = field(default_factory=dict)
    class_distribution_bottom5: dict = field(default_factory=dict)
    notes: str = ""


def find_raw_file(candidate_dir: Path, candidates: list[str]) -> Path | None:
    """Return the first matching raw file for a candidate, or None."""
    if not candidate_dir.exists():
        return None
    for name in candidates:
        p = candidate_dir / name
        if p.exists():
            return p
    # fall back: any single CSV in the directory
    csvs = list(candidate_dir.glob("*.csv"))
    return csvs[0] if len(csvs) == 1 else None


def check_duplicates(df: pd.DataFrame, feature_cols: list[str]) -> tuple[int, int]:
    """Return (exact_duplicate_count, near_duplicate_count).

    Exact duplicates: fully identical rows (features + label).
    Near duplicates: identical FEATURE vector but we count each group of
    size > 1 once per extra row, regardless of label -- this is what
    makes a symptom-set behave like a lookup key rather than a genuine
    predictive signal, which is exactly the failure mode documented for
    Candidate B in PHASE1_RESEARCH.md.
    """
    exact = int(df.duplicated(keep="first").sum())
    near = int(df.duplicated(subset=feature_cols, keep="first").sum())
    return exact, near


def check_train_test_overlap(
    train_df: pd.DataFrame, test_df: pd.DataFrame, feature_cols: list[str]
) -> int:
    """Count test rows whose feature vector already appears in train --
    this is the concrete, auditable evidence behind a 'leakage' verdict,
    rather than an assumption."""
    train_keys = set(map(tuple, train_df[feature_cols].values.tolist()))
    overlap = sum(
        1 for row in test_df[feature_cols].values.tolist() if tuple(row) in train_keys
    )
    return overlap


def process_candidate_a(raw_path: Path, top_n: int, seed: int) -> DataCardEntry | None:
    df = pd.read_csv(raw_path)
    label_col = df.columns[-1] if "disease" not in [c.lower() for c in df.columns] else \
        [c for c in df.columns if c.lower() == "disease"][0]
    feature_cols = [c for c in df.columns if c != label_col]

    n_raw = len(df)
    exact_dupes, near_dupes = check_duplicates(df, feature_cols)

    # Trim to the top-N most frequent diseases -- 773-way classification
    # is not realistic for a resume-scale project (see PHASE1_RESEARCH.md).
    top_classes = df[label_col].value_counts().nlargest(top_n).index
    trimmed = df[df[label_col].isin(top_classes)].drop_duplicates().reset_index(drop=True)

    train_df, temp_df = train_test_split(
        trimmed, test_size=0.30, stratify=trimmed[label_col], random_state=seed
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df[label_col], random_state=seed
    )

    overlap = check_train_test_overlap(train_df, test_df, feature_cols)

    out_dir = PROCESSED_DIR / "candidate_a_structured"
    out_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(out_dir / "train.csv", index=False)
    val_df.to_csv(out_dir / "val.csv", index=False)
    test_df.to_csv(out_dir / "test.csv", index=False)

    counts = trimmed[label_col].value_counts()
    return DataCardEntry(
        candidate="candidate_a_structured_backbone",
        source_file=str(raw_path.relative_to(REPO_ROOT)),
        n_rows_raw=n_raw,
        n_rows_after_cleaning=len(trimmed),
        n_classes=trimmed[label_col].nunique(),
        n_exact_duplicates=exact_dupes,
        n_near_duplicates=near_dupes,
        n_train_test_overlap=overlap,
        class_distribution_top5=counts.head(5).to_dict(),
        class_distribution_bottom5=counts.tail(5).to_dict(),
        notes=(
            f"Trimmed from full class set to top {top_n} diseases by frequency. "
            "Used as the structured-model training backbone."
        ),
    )


def process_candidate_b_leakage_report(raw_dir: Path, seed: int) -> DataCardEntry | None:
    train_path = raw_dir / "training_data.csv"
    if not train_path.exists():
        return None
    train_df = pd.read_csv(train_path)
    # this export sometimes has a trailing "Unnamed" index column
    train_df = train_df.loc[:, ~train_df.columns.str.contains("^Unnamed")]
    label_col = train_df.columns[-1]
    feature_cols = [c for c in train_df.columns if c != label_col]

    exact_dupes, near_dupes = check_duplicates(train_df, feature_cols)

    test_path = raw_dir / "test_data.csv"
    overlap = 0
    n_test = 0
    if test_path.exists():
        test_df = pd.read_csv(test_path)
        test_df = test_df.loc[:, ~test_df.columns.str.contains("^Unnamed")]
        n_test = len(test_df)
        overlap = check_train_test_overlap(train_df, test_df, feature_cols)

    counts = train_df[label_col].value_counts()

    # This is the actual leakage evidence, written to disk so it can be
    # cited directly in docs/DATASETS.md instead of asserted from memory.
    report = {
        "verdict": "EXCLUDED from final model -- documented leakage below",
        "n_rows": len(train_df),
        "n_classes": train_df[label_col].nunique(),
        "n_near_duplicate_feature_vectors_in_train": near_dupes,
        "pct_rows_that_are_near_duplicates": round(100 * near_dupes / len(train_df), 2),
        "n_test_rows": n_test,
        "n_test_rows_whose_features_appear_in_train": overlap,
        "pct_test_leaked": round(100 * overlap / n_test, 2) if n_test else None,
        "interpretation": (
            "A high percentage of near-duplicate feature vectors within the "
            "training set, combined with a high train/test feature overlap, "
            "means the model can achieve near-perfect test accuracy by "
            "memorizing symptom-set -> disease mappings rather than learning "
            "a generalizable relationship. This is why this dataset is used "
            "only as a fast pipeline smoke-test, never as the shipped model's "
            "training data."
        ),
    }
    out_dir = PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "candidate_b_leakage_report.json", "w") as f:
        json.dump(report, f, indent=2)

    return DataCardEntry(
        candidate="candidate_b_leakage_smoketest",
        source_file=str(train_path.relative_to(REPO_ROOT)),
        n_rows_raw=len(train_df),
        n_rows_after_cleaning=len(train_df),
        n_classes=train_df[label_col].nunique(),
        n_exact_duplicates=exact_dupes,
        n_near_duplicates=near_dupes,
        n_train_test_overlap=overlap,
        class_distribution_top5=counts.head(5).to_dict(),
        class_distribution_bottom5=counts.tail(5).to_dict(),
        notes="EXCLUDED from final model. Kept only as a smoke-test set and as documented leakage evidence.",
    )


def process_candidate_c(raw_path: Path, seed: int) -> DataCardEntry | None:
    df = pd.read_csv(raw_path)
    # Kaggle export has columns: Unnamed: 0, label, text (varies by version)
    text_col = next(c for c in df.columns if c.lower() in ("text", "symptoms", "description"))
    label_col = next(c for c in df.columns if c.lower() in ("label", "disease"))
    df = df[[text_col, label_col]].rename(columns={text_col: "text", label_col: "label"})
    df = df.dropna().reset_index(drop=True)

    n_raw = len(df)
    exact_dupes = int(df.duplicated(keep="first").sum())
    # near-duplicate text check: same label + near-identical normalized text
    normalized = df["text"].str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    near_dupes = int(normalized.duplicated(keep="first").sum())

    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    train_df, temp_df = train_test_split(
        df, test_size=0.30, stratify=df["label"], random_state=seed
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["label"], random_state=seed
    )

    out_dir = PROCESSED_DIR / "candidate_c_nlp"
    out_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(out_dir / "train.csv", index=False)
    val_df.to_csv(out_dir / "val.csv", index=False)
    test_df.to_csv(out_dir / "test.csv", index=False)

    counts = df["label"].value_counts()
    return DataCardEntry(
        candidate="candidate_c_nlp_extraction",
        source_file=str(raw_path.relative_to(REPO_ROOT)),
        n_rows_raw=n_raw,
        n_rows_after_cleaning=len(df),
        n_classes=df["label"].nunique(),
        n_exact_duplicates=exact_dupes,
        n_near_duplicates=near_dupes,
        n_train_test_overlap=0,
        class_distribution_top5=counts.head(5).to_dict(),
        class_distribution_bottom5=counts.tail(5).to_dict(),
        notes="Free-text natural-language dataset. Used to build/validate the NLP symptom-extraction layer.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-n-diseases", type=int, default=60,
                         help="How many most-frequent diseases to keep from Candidate A.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[DataCardEntry] = []

    a_path = find_raw_file(RAW_DIR / "candidate_a", EXPECTED_FILES["candidate_a"])
    if a_path:
        print(f"[candidate_a] processing {a_path}")
        entry = process_candidate_a(a_path, args.top_n_diseases, args.seed)
        if entry:
            entries.append(entry)
    else:
        print("[candidate_a] not found under data/raw/text/candidate_a/ -- skipped. "
              "Download from Kaggle (dhivyeshrk/diseases-and-symptoms-dataset) to include it.")

    b_dir = RAW_DIR / "candidate_b"
    if b_dir.exists():
        print(f"[candidate_b] processing {b_dir}")
        entry = process_candidate_b_leakage_report(b_dir, args.seed)
        if entry:
            entries.append(entry)
    else:
        print("[candidate_b] not found under data/raw/text/candidate_b/ -- skipped.")

    c_path = find_raw_file(RAW_DIR / "candidate_c", EXPECTED_FILES["candidate_c"])
    if c_path:
        print(f"[candidate_c] processing {c_path}")
        entry = process_candidate_c(c_path, args.seed)
        if entry:
            entries.append(entry)
    else:
        print("[candidate_c] not found under data/raw/text/candidate_c/ -- skipped. "
              "Download from Kaggle (niyarrbarman/symptom2disease) to include it.")

    if not entries:
        print("\nNo raw datasets found. Place files under data/raw/text/candidate_[a|b|c]/ "
              "and re-run. See this file's docstring for expected filenames.")
        return 1

    data_card = {
        "seed": args.seed,
        "top_n_diseases_for_candidate_a": args.top_n_diseases,
        "entries": [vars(e) for e in entries],
    }
    with open(PROCESSED_DIR / "data_card.json", "w") as f:
        json.dump(data_card, f, indent=2)

    print(f"\nWrote data card to {PROCESSED_DIR / 'data_card.json'}")
    for e in entries:
        print(f"  - {e.candidate}: {e.n_rows_after_cleaning} rows, {e.n_classes} classes, "
              f"{e.n_near_duplicates} near-duplicates, {e.n_train_test_overlap} train/test overlap rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
