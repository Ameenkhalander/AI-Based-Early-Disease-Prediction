"""prepare_dataset.py (vision)

WHY: downloads/loads BOTH image datasets and prepares them as two
     independent training sets (never merged):
        --dataset ham10000  -> data/processed/vision/lesion/
        --dataset dermnet   -> data/processed/vision/general/
     Applies the standard train/val/test split, records class counts
     (to quantify HAM10000's severe nevus-dominant imbalance and
     DermNet's per-class counts), and writes a data_card.json per dataset.
"""

# Implementation added in Phase 12.
