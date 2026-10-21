# Data Dictionary

This data dictionary outlines every feature, target, and metadata field across our tables, detailing its calculation formula, source, availability timeline, and feature eligibility.

## Core Conventions
* **Execution Timing:** All predictions and feature lookups are assumed to occur **after the market close on date $T$**.
* **Trading-Day Offsets:** $T$ represents the observation session date. $T+11$ to $T+15$ represent the 3rd trading week following session $T$.
* **Adjusted Prices:** All price calculations utilize adjusted close series (`Close`) to account for splits and dividends.
* **Missing Future Observations:** Rows where the 5-day forward window ($T+11$ to $T+15$) is incomplete (e.g., near the end of the historical time series) are strictly excluded from receiving target labels.

---

## Field Specifications

| Field Name | Data Type | Formula / Definition | Source | Available When? | Model Feature? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Ticker` | String | Canonical asset symbol (e.g., `HDFCBANK.NS`) | Yahoo Finance | Immediately upon ingest | **Yes** (as categorical/identifier) |
| `Date` | Date | Session trading date $T$ (normalized timezone-free) | Exchange Calendar | Immediately upon ingest | **Yes** (chronological index) |
| `Close` | Float | Session closing price adjusted for splits/dividends | Yahoo Finance | After market close on $T$ | **Yes** |
| `Daily_Return` | Float | $\frac{\text{Close}_T}{\text{Close}_{T-1}} - 1$ | Calculated from `Close` | After market close on $T$ | **Yes** |
| `SMA_20` | Float | $\frac{1}{20} \sum_{i=0}^{19} \text{Close}_{T-i}$ | Calculated from `Close` | After market close on $T$ | **Yes** |
| `SMA_50` | Float | $\frac{1}{50} \sum_{i=0}^{49} \text{Close}_{T-i}$ | Calculated from `Close` | After market close on $T$ | **Yes** |
| `Volume_SMA_20` | Float | $\frac{1}{20} \sum_{i=0}^{19} \text{Volume}_{T-i}$ | Calculated from `Volume` | After market close on $T$ | **Yes** |
| `Max_Close_T11_T15` | Float | $\max(\text{Close}_{T+11}, \ldots, \text{Close}_{T+15})$ | Future Price Series | Only after session $T+15$ completes | **No (Leakage Risk)** |
| `Max_Return_T11_T15` | Float | $\frac{\text{Max\_Close}_{T+11:T+15}}{\text{Close}_T} - 1$ | Calculated from Future Prices | Only after session $T+15$ completes | **No (Leakage Risk)** |
| `Target` | Integer | $\mathbb{1}\left[\max(P_{T+11},\ldots,P_{T+15}) \ge 1.05P_T\right]$ | Derived Target Logic | Only after session $T+15$ completes | **No (Label)** |
