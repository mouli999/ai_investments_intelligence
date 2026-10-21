# Data Dictionary

This data dictionary outlines every field, target, and metadata table across our pipeline, detailing its calculation formula, source, availability timeline, price-adjustment convention, storage status, and strict role in our machine learning architecture.

---

## Price-Adjustment Convention & Governance

To maintain mathematical consistency across historical technical indicators and prevent artificial price shocks during corporate actions, our pipeline adheres to a strict price-adjustment convention:

1. **Adjusted Close Standard (`Close`):** 
   - All price-based features (`SMA_20`, `SMA_50`, `Daily_Return`, and future window returns) are calculated exclusively using the **adjusted close price** series provided by Yahoo Finance (`yfinance`).
   - *Definition:* The adjusted close incorporates back-calculated adjustments for corporate actions such as stock splits, bonus issues, and dividend payouts.
2. **Avoiding Distortion in Moving Averages:** 
   - By utilizing split- and dividend-adjusted closing prices, our moving averages (`SMA_20`, `SMA_50`) reflect true economic returns rather than artificial discontinuities caused by corporate restructurings.
3. **Point-in-Time Integrity & Backward-Looking Adjustments:** 
   - While adjusted close series incorporate retrospective adjustments for corporate events, our feature lookback window ($T-250$ to $T$) uses only information finalized at or before observation date $T$. 
   - Forward return calculations ($T+11$ to $T+15$) strictly measure subsequent realized price movements relative to the close at $T$, maintaining absolute chronological separation.

---

## Core Architectural Design Definitions

To maintain a rigorous quantitative pipeline, every column falls into one of four mutually exclusive categories:
1. **Identifiers & Keys (`ID`):** Fields used to index, group, or uniquely identify rows (e.g., `Ticker`, `Date`). While they may be passed to models as categorical groupings or entity embeddings, they are **not** mathematical features derived from market dynamics.
2. **Model Features (`Feature`):** Calculated quantitative attributes derived strictly from historical data available at or before observation date $T$. These are supplied as input variables to the machine learning model.
3. **Target / Audit Fields (`Target` / `Audit`):** Future-derived outcomes used exclusively for training supervision and performance evaluation. **Strictly prohibited as model inputs** to prevent look-ahead bias and data leakage.
4. **Metadata Fields (`Metadata`):** Attributes describing provenance, source provider, or ingestion timestamps.

---

## Field Specifications & Role Classification

| Field Name | Data Type | Formula / Definition | Source | Available When? | Architectural Role | Model Feature? | Storage Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Ticker` | String | Canonical asset symbol (e.g., `HDFCBANK.NS`) | Yahoo Finance | Immediately upon ingest | **Identifier / Key** | **No** *(Used for grouping/indexing only)* | Stored in CSVs |
| `Date` | Date | Session trading date $T$ (normalized timezone-free) | Exchange Calendar | Immediately upon ingest | **Identifier / Chronological Index** | **No** *(Used for sorting/splitting only)* | Stored in CSVs |
| `Close` | Float | Session closing price **adjusted for splits and dividends** | Yahoo Finance | After market close on $T$ | **Adjusted Market Data / Base Price** | **Yes** *(Or transformed into returns)* | Stored in CSVs |
| `Daily_Return` | Float | $\frac{\text{Close}_T}{\text{Close}_{T-1}} - 1$ (using adjusted close) | Calculated from `Close` | After market close on $T$ | **Model Feature** | **Yes** | Stored in CSVs |
| `SMA_20` | Float | $\frac{1}{20} \sum_{i=0}^{19} \text{Close}_{T-i}$ (using adjusted close) | Calculated from `Close` | After market close on $T$ | **Model Feature** | **Yes** | Stored in CSVs |
| `SMA_50` | Float | $\frac{1}{50} \sum_{i=0}^{49} \text{Close}_{T-i}$ (using adjusted close) | Calculated from `Close` | After market close on $T$ | **Model Feature** | **Yes** | Stored in CSVs |
| `Volume_SMA_20` | Float | $\frac{1}{20} \sum_{i=0}^{19} \text{Volume}_{T-i}$ | Calculated from `Volume` | After market close on $T$ | **Model Feature** | **Yes** | Stored in CSVs |
| `Max_Close_T11_T15` | Float | $\max(\text{Close}_{T+11}, \ldots, \text{Close}_{T+15})$ (using adjusted close) | Future Price Series | Only after session $T+15$ completes | **Audit / Target Component** | **No (Leakage Risk)** | Stored in CSVs |
| `Max_Return_T11_T15` | Float | $\frac{\text{Max\_Close}_{T+11:T+15}}{\text{Close}_T} - 1$ (using adjusted close) | Calculated from Future Prices | Only after session $T+15$ completes | **Audit / Target Component** | **No (Leakage Risk)** | Stored in CSVs |
| `Target` | Integer | $\mathbb{1}\left[\max(P_{T+11},\ldots,P_{T+15}) \ge 1.05P_T\right]$ | Derived Target Logic | Only after session $T+15$ completes | **Supervised Learning Label** | **No (Label Only)** | Stored in CSVs |
| `Data_Source` | String | Provider identifier (e.g., `yfinance`) | Ingestion Engine | Immediately upon ingest | **Metadata** | **No** | **[Proposed / Not Yet Stored]** |
| `Retrieved_At` | Timestamp | Timestamp recording when the raw payload was fetched | Ingestion Engine | Immediately upon ingest | **Metadata** | **No** | **[Proposed / Not Yet Stored]** |
