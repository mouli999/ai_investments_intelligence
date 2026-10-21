import os
import pandas as pd

def process_raw_stock_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    if not os.path.exists(raw_dir):
        print("❌ Raw data directory not found.")
        return
        
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    if not raw_files:
        print("❌ No raw CSV files found.")
        return

    # --- SELECT ONLY THE LATEST RAW FILE PER TICKER ---
    # Group raw files by their base ticker name to find the most recent date stamp
    latest_files_map = {}
    for filename in raw_files:
        # Example filename: HDFCBANK_NS_raw_2026-10-21.csv -> Base: HDFCBANK_NS
        if "_raw_" in filename:
            ticker_base = filename.split("_raw_")[0]
            # Files are date-stamped, so sorting alphabetically or by filename string gives the latest date
            if ticker_base not in latest_files_map or filename > latest_files_map[ticker_base]:
                latest_files_map[ticker_base] = filename

    target_raw_files = list(latest_files_map.values())
    print(preprocessing_log := f"🎯 Identified latest raw snapshots to process: {target_raw_files}\n")

    # Optional: Clean up existing processed files to avoid stale data clutter
    for filename in os.listdir(processed_dir):
        if filename.endswith(".csv"):
            try:
                os.remove(os.path.join(processed_dir, filename))
            except Exception:
                pass
    # ------------------------------------------------

    for filename in target_raw_files:
        file_path = os.path.join(raw_dir, filename)
        print(f"Processing latest snapshot: {filename}...")
        
        df = pd.read_csv(file_path)
        
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            if df["Date"].dt.tz is not None:
                df["Date"] = df["Date"].dt.tz_localize(None)
            df = df.sort_values("Date").reset_index(drop=True)
        
        df["Daily_Return"] = df["Close"].pct_change()
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()
        
        # Save processed file using clean naming convention
        ticker_base = filename.split('_raw_')[0].upper()
        processed_filename = f"{ticker_base}_processed.csv"
        processed_path = os.path.join(processed_dir, processed_filename)
        
        df.to_csv(processed_path, index=False)
        print(f"✅ Saved processed data to: {processed_path} (Total rows: {len(df)})")

if __name__ == "__main__":
    process_raw_stock_data()
    