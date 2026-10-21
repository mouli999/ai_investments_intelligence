# Data Quality Rules & Validation Checklist

To maintain institutional-grade data integrity across our quantitative pipeline, the dataset must adhere to the following seven quality rules.

## Quality Rule Checklist

- [x] **1. Unique Observations**
  - **Rule:** No duplicate `(Ticker, Date)` pairs are permitted in processed or ML-ready datasets.
  - **Enforcement:** Automated assertion (`assert not master_df.duplicated(subset=["Ticker", "Date"]).any()`) in `dataset_builder.py`.

- [x] **2. Valid Prices**
  - **Rule:** All OHLC prices must be strictly positive ($> 0$), and session High must be greater than or equal to session Low ($\text{High} \ge \text{Low}$).
  - **Enforcement:** Validated during raw-to-processed ingestion and preprocessing checks.

- [x] **3. Consistent Identifiers**
  - **Rule:** Only clean canonical ticker symbols are used (e.g., `HDFCBANK.NS`, `INFY.NS`, `RELIANCE.NS`, `TCS.NS`, `^NSEI`). Raw file naming artifacts or date suffixes are strictly stripped.
  - **Enforcement:** Enforced via explicit canonical whitelists in processing and dataset-building scripts.

- [x] **4. Date Ordering**
  - **Rule:** Records must be strictly sorted in ascending chronological order within each ticker series.
  - **Enforcement:** `df = df.sort_values("Date").reset_index(drop=True)` executed across all processing modules.

- [x] **5. Missing Values & Window Completeness**
  - **Rule:** Missing feature values due to rolling lookbacks (e.g., 50-day SMA warm-up) must be dropped or explicitly documented. Incomplete future return windows ($T+11$ to $T+15$) must never receive target labels.
  - **Enforcement:** `dropna()` filters applied on feature lookbacks and future return arrays.

- [x] **6. Zero Look-Ahead Bias / No Leakage**
  - **Rule:** Future-derived target columns (`Max_Close_T11_T15`, `Max_Return_T11_T15`, and `Target`) must be strictly segregated from the model feature matrix.
  - **Enforcement:** Excluded from the model feature allowlist during feature matrix preparation.

- [x] **7. Reproducibility & Provenance**
  - **Rule:** Data sources (`yfinance`), retrieval timestamps, snapshot versions, and processing assumptions must be documented and version-controlled.
  - **Enforcement:** Timestamped raw snapshots stored in `data/raw/` and documented in project reports.