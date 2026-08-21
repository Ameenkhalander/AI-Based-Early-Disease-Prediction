# Datasets

Full research/reasoning is in PHASE1_RESEARCH.md. This file tracks
VERIFIED findings from actually running ml/*/prepare_dataset.py --
updated as each candidate's raw data becomes available.

## Text: how to get the raw data

This project's sandbox environment could not reach kaggle.com directly,
so the raw Candidate A and Candidate C exports must be downloaded on
your machine and dropped into the repo:

```bash
pip install kaggle   # requires a kaggle.json API token in ~/.kaggle/

kaggle datasets download -d dhivyeshrk/diseases-and-symptoms-dataset -p data/raw/text/candidate_a --unzip
kaggle datasets download -d niyarrbarman/symptom2disease -p data/raw/text/candidate_c --unzip

python ml/text/prepare_dataset.py
```

Candidate B (kaushil268) does not need a Kaggle account -- a GitHub
mirror with the identical 132-symptom/42-disease schema was used
instead, and is already processed below.

## Candidate B -- VERIFIED leakage findings (ran 2026-08-21)

Source used: GitHub mirror of the same 132-symptom/42-disease dataset
(`anujdutt9/Disease-Prediction-from-Symptoms`), since the underlying
Kaggle dataset (`kaushil268/disease-prediction-using-machine-learning`)
was unreachable from this sandbox. Same schema, same known dataset.

| Metric | Value |
|---|---|
| Rows | 4,920 |
| Classes | 41 |
| Near-duplicate feature vectors in training set | 4,616 (**93.8%**) |
| Test rows whose feature vector already exists in train | 41 / 42 (**97.6%**) |

**Verdict confirmed with evidence, not just asserted:** this is
effectively a lookup table. A model can hit ~100% test accuracy by
memorizing symptom-set -> disease pairs. **Excluded from the shipped
model.** Full machine-readable report:
`data/processed/text/candidate_b_leakage_report.json`. Retained only as
a fast pipeline smoke-test dataset (which is how it was used here, to
prove `prepare_dataset.py` works end-to-end before Candidate A/C were
available).

## Candidate A -- structured backbone

Not yet processed in this environment (raw file not reachable). Run the
download command above, then `python ml/text/prepare_dataset.py` --
`data/processed/text/data_card.json` will be updated automatically with
real row/class counts and duplicate-check results for Candidate A on
your next run.

## Candidate C -- NLP extraction validation set

Same status as Candidate A -- pending your local Kaggle download.

## Phase 4 baseline training -- VERIFIED smoke-test run (ran 2026-08-21)

Ran `ml/text/train_baseline.py --data-dir data/processed/text/candidate_b_smoketest --smoke-test`
(Logistic Regression, Random Forest, XGBoost) purely to prove the
training/evaluation code works end-to-end, using the already-known-leaky
Candidate B data. Results are NOT the real Phase 4 benchmark and are
explicitly tagged `smoke_test: true` in
`artifacts/text_model/candidates/smoketest_comparison.json` so they can
never be confused with the real Candidate A numbers later.

| Model | Test accuracy | Test F1 (macro) |
|---|---|---|
| Logistic Regression | **100.0%** (flagged automatically as suspicious) | 1.000 |
| Random Forest | 97.6% | 0.984 |
| XGBoost | 97.6% | 0.984 |

This is the leakage from the earlier duplicate-check finding surfacing
directly in model performance -- exactly the failure mode
`ml/common/metrics.py` is designed to catch automatically (any test
accuracy over 98% triggers a written warning in the evaluation report,
not just a comment in this doc). The real Phase 4 numbers on the
Candidate A backbone (once downloaded) are expected to be meaningfully
lower than 97-100% -- and that will be a sign the model is doing real
work, not memorizing.

## Images (HAM10000 / DermNet)

Not yet processed -- Phase 12. `ml/vision/prepare_dataset.py` will
follow the same pattern: real duplicate/imbalance checks written to a
data card, not assumed from the literature review in PHASE1_RESEARCH.md.
