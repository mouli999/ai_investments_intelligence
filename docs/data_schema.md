# Data Schema Specification

This document defines the logical data schema for the AI-Powered Financial Intelligence Engine. It establishes a strict separation between raw market data, point-in-time model features, and future target labels to prevent look-ahead bias and data leakage.

---

## Table A — `daily_prices` (Raw Ingested Data)
* **Scope:** One row per ticker per trading session date.
* **Storage Path:** `data/raw/`
* **Primary Key:** `(ticker, date)`

| Column Name | Data Type | Description / Meaning |
| :--- | :--- | :--- |
| `Date` / `date` | Timestamp / Date | Trading session date (normalized to midnight) |
| `Open` / `open` | Float | Opening price of the asset for the trading session |
| `High` / `high` | Float | Highest traded price during the session |
| `Low` / `low` | Float | Lowest traded price during the session |
| `Close` / `close` | Float | Adjusted closing price accounting for corporate actions and dividends |
| `Volume` / `volume` | Integer | Total shares or units traded during the session |
| `Data_Source` / `data_source` | String | Provider identifier (e.g., `yfinance`) |
| `Retrieved_At` / `retrieved_at` | Timestamp | Timestamp recording when the raw payload was fetched |

---

## Table B — `market_features` (Model Feature Matrix)
* **Scope:** One row per ticker per prediction date $T$. Derived strictly from information available at or before observation date $T$.
* **Storage Path:** `data/processed/` & `data/ml_ready/`
* **Primary Key:** `(ticker, date)`

| Column Name | Data Type | Description / Meaning |
| :--- | :--- | :--- |
| `Ticker` / `ticker` | String | Canonical symbol (e.g., `HDFCBANK.NS`, `RELIANCE.NS`) |
| `Date` / `date` | Timestamp / Date | Observation / prediction date $T$ |
| `Close` / `close` | Float | Closing price at date $T$ |
| `Daily_Return` | Float | One-session percentage return ($P_T / P_{T-1} - 1$) |
| `SMA_20` | Float | 20-session simple moving average of closing prices |
| `SMA_50` | Float | 50-session simple moving average of closing prices |
| `Volume_SMA_20` | Float | 20-session rolling average trading volume |

---

## Table C — `prediction_labels` (Target & Audit Fields)
* **Scope:** Future outcomes used exclusively for model training supervision and auditing. **Strictly prohibited as model inputs.**
* **Storage Path:** `data/ml_ready/point_in_time_features_targets.csv`
* **Primary Key:** `(ticker, prediction_date)`

| Column Name | Data Type | Description / Meaning |
| :--- | :--- | :--- |
| `Max_Close_T11_T15` | Float | Maximum closing price across the $T+11$ to $T+15$ trading window |
| `Max_Return_T11_T15` | Float | Maximum future return relative to close at $T$ ($P_{\max} / P_T - 1$) |
| `Target` | Integer | Binary label: `1` if $\max(P_{T+11},\ldots,P_{T+15}) \ge 1.05 \times P_T$, else `0` |
