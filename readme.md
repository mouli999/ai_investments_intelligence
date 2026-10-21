# AI-Powered Financial Intelligence Engine

A point-in-time predictive classification engine for Indian equities designed to identify medium-term directional outperformance.

## Project Structure

- `data/raw/`: downloaded historical stock data
- `data/processed/`: cleaned stock data with calculated features
- `data/ml_ready/`: combined features and target labels for modeling
- `data/reports/`: stock screener CSV reports
- `src/`: scripts for data ingestion, processing, screening, and dataset creation
- `notebooks/`: exploratory data analysis and experiments
- `tests/`: validation and unit tests
- `config/`: configuration files and universe definitions

## Setup

Run commands from the repository root:

```powershell
python -m pip install -r requirements.txt
```

The scripts use paths relative to the current working directory, so run them from the repository root.

## Data Pipeline

Run these scripts in order:

```powershell
python .\src\ingest_data.py
python .\src\process_data.py
python .\src\screener.py
python .\src\dataset_builder.py
```

1. **`ingest_data.py`** downloads approximately six months of historical data for the watchlist defined in the script and saves CSV files under `data/raw/`. It uses Yahoo Finance through `yfinance`.
2. **`process_data.py`** reads raw CSV files, calculates daily returns, 20-day and 50-day simple moving averages, and 20-day average volume, then writes processed CSV files to `data/processed/`.
3. **`screener.py`** evaluates the latest processed data. A stock qualifies when its average volume is above 100,000 and its close is above its 20-day SMA, which is above its 50-day SMA. It prints the results and saves a dated report under `data/reports/`.
4. **`dataset_builder.py`** combines processed stock files into `data/ml_ready/point_in_time_features_targets.csv`. Its target is `1` when any closing price from T+11 through T+15 is at least 5% above the close on T; otherwise the target is `0`. Rows without the full five-trading-day evaluation window are excluded. The Nifty 50 file is not used to calculate this target.

## Alpha Vantage API Check

`src/test.py` checks connectivity to Alpha Vantage and requests daily data for `RELIANCE.BSE`. Set an API key in the environment before running it:

```powershell
$env:ALPHAVANTAGE_API_KEY = "your-api-key"
python .\src\test.py
```

Do not commit API keys to source control. If a key was previously committed or shared, revoke it and create a replacement.

## Dependencies

Dependencies are listed in `requirements.txt`. The ingestion script requires `yfinance`; install all project dependencies with the setup command above.
