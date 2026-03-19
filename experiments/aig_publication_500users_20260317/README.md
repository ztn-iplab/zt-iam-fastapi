# AIg Dataset

This directory contains the public AIg calibration dataset prepared for external release.

## Files

- `aig_publication_dataset.csv`: row-level dataset for AIg calibration and model benchmarking
- `DATASET_CARD.md`: dataset description, schema, and release notes

## Reproducibility

The dataset can be loaded directly with standard Python tooling such as `pandas`, `pyarrow`, or `csv`. Example:

```bash
python scripts/compare_aig_models.py \
  --dataset-csv experiments/aig_publication_500users_20260317/aig_publication_dataset.csv \
  --output-dir /tmp/aig_model_bench
```
