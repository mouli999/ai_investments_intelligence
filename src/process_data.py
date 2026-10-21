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
    
    for filename in raw_files:
        file_path = os.path.join(raw_dir, filename)
        print(f"Processing {filename}...")
        
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