import os
import pandas as pd

def normalize_trading_dates(date_values):
    dates = pd.to_datetime(date_values)
    if dates.dt.tz is not None:
        dates = dates.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    return dates.dt.normalize()

def build_point_in_time_dataset():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, "data", "processed")
    dataset_dir = os.path.join(project_root, "data", "ml_ready")
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Explicit Whitelist of Canonical Stock Files to prevent duplicate history bugs
    canonical_stock_files = [
        "HDFCBANK_NS_processed.csv",
        "INFY_NS_processed.csv",
        "RELIANCE_NS_processed.csv",
        "TCS_NS_processed.csv"
    ]
    
    processed_files = [
        filename for filename in canonical_stock_files
        if os.path.exists(os.path.join(processed_dir, filename))
    ]
    
    all_stock_data = []
    
    print("⚙️ Constructing Point-in-Time dataset with explicit canonical whitelist & T+11 to T+15 target...\n")
    
    for filename in processed_files:
        file_path = os.path.join(processed_dir, filename)
        df = pd.read_csv(file_path)
        
        if df.empty:
            continue
            
        ticker_prefix = filename.split('_processed')[0]
        ticker_name = ticker_prefix.replace('_', '.')
        
        df["Date"] = normalize_trading_dates(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        
        # Compare highest close in T+11...T+15 with 105% of close at T
        future_closes = pd.concat(
            [df["Close"].shift(-offset) for offset in range(11, 16)],
            axis=1,
        )
        complete_window = future_closes.notna().all(axis=1)
        df["Max_Close_T11_T15"] = future_closes.max(axis=1).where(complete_window)
        df["Max_Return_T11_T15"] = df["Max_Close_T11_T15"] / df["Close"] - 1
        threshold_hit = future_closes.ge(df["Close"] * 1.05, axis="index").any(axis=1)
        df["Target"] = (complete_window & threshold_hit).astype(int)
        
        df["Ticker"] = ticker_name
        
        # Exclude incomplete forward windows and rows without the 50-day feature history
        df_ml = df.dropna(subset=["Max_Return_T11_T15", "SMA_50"]).copy()
        
        cols_to_keep = [
            "Date", "Ticker", "Close", "SMA_20", "SMA_50", "Volume_SMA_20", 
            "Max_Close_T11_T15", "Max_Return_T11_T15", "Target"
        ]
        all_stock_data.append(df_ml[cols_to_keep])
        
    if all_stock_data:
        master_df = pd.concat(all_stock_data, ignore_index=True)
        
        # --- DATASET INTEGRITY ASSERTIONS ---
        assert not master_df.duplicated(subset=["Ticker", "Date"]).any(), "❌ Integrity Error: Duplicate Ticker-Date observations found!"
        
        expected_tickers = {"HDFCBANK.NS", "INFY.NS", "RELIANCE.NS", "TCS.NS"}
        actual_tickers = set(master_df["Ticker"].unique())
        assert actual_tickers == expected_tickers, f"❌ Integrity Error: Unexpected tickers found! Got {actual_tickers}"
        
        dataset_path = os.path.join(dataset_dir, "point_in_time_features_targets.csv")
        master_df.to_csv(dataset_path, index=False)
        
        print(f"✅ Successfully generated audit-ready ML dataset!")
        print(f"📂 Saved to: {dataset_path}")
        print(f"📊 Total valid training rows: {len(master_df)} across tickers: {actual_tickers}")
        print(f"🎯 Target Distribution:\n{master_df['Target'].value_counts()}")
        print("\n--- Sample Snapshot ---")
        print(master_df[["Date", "Ticker", "Close", "Max_Close_T11_T15", "Max_Return_T11_T15", "Target"]].tail(3))
    else:
        print("❌ No valid stock data processed.")

if __name__ == "__main__":
    build_point_in_time_dataset()