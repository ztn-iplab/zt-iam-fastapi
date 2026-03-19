# Dataset Card

## Summary

This dataset contains decision-state rows for Actor Integrity (AIg) calibration. Each row corresponds to a protected-action decision point together with current evidence, prior confidence state, and short-history continuity features.

## File

- `aig_publication_dataset.csv`

## Row semantics

Each row represents one protected-action decision point.

## Main column groups

- identifiers:
  - `campaign_id`
  - `split`
  - `session_id`
  - `action_id`
  - `scenario`
  - `action_name`
- current decision-state features:
  - `delta_t_minutes`
  - `prev_confidence`
  - `e_telecom`
  - `e_device`
  - `e_timing`
  - `e_ordering`
- short-history features:
  - `session_step_index`
  - `recent_conf_mean_3`
  - `recent_conf_slope_3`
  - `recent_delta_mean_3`
  - `recent_telecom_mean_3`
  - `recent_device_mean_3`
  - `recent_timing_mean_3`
  - `recent_ordering_mean_3`
  - `steps_since_strong_telecom`
  - `minutes_since_strong_telecom`
- labels and analytical-baseline fields:
  - `aig_label`
  - `manual_allow`
  - `manual_threshold`
  - `manual_c_value`

## Privacy and release notes

- The dataset contains no real participant names.
- The dataset contains no local filesystem paths.
- The dataset contains no machine names.
- The dataset contains no manuscript result tables.
- The dataset is intended for reproducible calibration and benchmarking of AIg models.

## Usage note

Rows are decision-state examples, not raw telecom logs or raw client telemetry. Intermediate runtime events were used to derive features but are not included in this public release.
