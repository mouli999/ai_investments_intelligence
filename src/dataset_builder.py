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
    
    nifty_path = os.path.join(processed_dir, "NSEI_processed.csv")
    if not os.path.exists(nifty_path):
        print("❌ Benchmark (NSEI_processed.csv) not found! Run ingestion and processing first.")
        return
        
    # Load and prepare Benchmark (Nifty 50) cumulative forward returns (T+10 to T+15)
    nifty_df = pd.read_csv(nifty_path)
    nifty_df["Date"] = normalize_trading_dates(nifty_df["Date"])
    nifty_df = nifty_df.sort_values("Date").reset_index(drop=True)
    
    # R_nifty = P_{T+15} / P_{T+10} - 1
    # In pandas indexing: shift(-15) is P_{T+15} relative to index T, but let's align strictly:
    # Price at T+10 is close.shift(-10), Price at T+15 is close.shift(-15)
    nifty_df["Benchmark_Return_T10_T15"] = (nifty_df["Close"].shift(-15) / nifty_df["Close"].shift(-10)) - 1
    
    benchmark_lookup = nifty_df[["Date", "Benchmark_Return_T10_T15"]].copy()
    
    processed_files = [f for f in os.listdir(processed_dir) if f != "NSEI_processed.csv" and f.endswith('.csv')]
    all_stock_data = []
    
    print("⚙️ Constructing Point-in-Time dataset with true cumulative T+10 to T+15 returns...\n")
    
    for filename in processed_files:
        file_path = os.path.join(processed_dir, filename)
        df = pd.read_csv(file_path)
        
        if df.empty:
            continue
            
        # Fix Ticker Name Parsing cleanly from filename (e.g. RELIANCE_NS_processed.csv -> RELIANCE.NS)
        ticker_prefix = filename.split('_processed')[0]
        ticker_name = ticker_prefix.replace('_', '.')
        
        df["Date"] = normalize_trading_dates(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        
        # --- CUMULATIVE FORWARD RETURN (T+10 to T+15) ---
        # R_stock = (Close at T+15 / Close at T+10) - 1
        df["Stock_Return_T10_T15"] = (df["Close"].shift(-15) / df["Close"].shift(-10)) - 1
        
        # Merge with Nifty benchmark returns by Date
        df = pd.merge(df, benchmark_lookup, on="Date", how="left")
        
        # Buffer threshold: 5.0% outperformance + 0.5% taxes/slippage = 5.5% (0.055)
        buffer_threshold = 0.055
        
        # Target assignment: Stock Return >= Benchmark Return + 5.5%
        df["Target"] = (df["Stock_Return_T10_T15"] >= (df["Benchmark_Return_T10_T15"] + buffer_threshold)).astype(int)
        
        df["Ticker"] = ticker_name
        
        # --- FIX ISSUE #2: Drop incomplete future windows & warm-up NaNs ---
        # Explicitly drop rows where future returns or SMA_50 are NaN
        df_ml = df.dropna(subset=["Stock_Return_T10_T15", "Benchmark_Return_T10_T15", "SMA_50"]).copy()
        
        cols_to_keep = [
            "Date", "Ticker", "Close", "SMA_20", "SMA_50", "Volume_SMA_20", 
            "Stock_Return_T10_T15", "Benchmark_Return_T10_T15", "Target"
        ]
        df_ml = df_ml[cols_to_keep]
        all_stock_data.append(df_ml)
        
    if all_stock_data:
        master_df = pd.concat(all_stock_data, ignore_index=True)
        dataset_path = os.path.join(dataset_dir, "point_in_time_features_targets.csv")
        master_df.to_csv(dataset_path, index=False)
        
        print(f"✅ Successfully generated audit-ready ML dataset!")
        print(f"📂 Saved to: {dataset_path}")
        print(f"📊 Total valid training rows: {len(master_df)}")
        print(f"🎯 Target Distribution:\n{master_df['Target'].value_counts()}")
        print("\n--- Sample Snapshot ---")
        print(master_df[["Date", "Ticker", "Stock_Return_T10_T15", "Benchmark_Return_T10_T15", "Target"]].tail(3))
    else:
        print("❌ No data processed.")

if __name__ == "__main__":
    build_point_in_time_dataset()

    