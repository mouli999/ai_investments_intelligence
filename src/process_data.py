import os
import pandas as pd

def process_raw_stock_data():
    raw_dir = os.path.join("data", "raw")
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Check if raw directory exists and has files
    if not os.path.exists(raw_dir):
        print("❌ Raw data directory not found. Please run Day 4 ingestion first.")
        return
        
    raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not raw_files:
        print("❌ No raw CSV files found in data/raw/.")
        return
        
    for filename in raw_files:
        file_path = os.path.join(raw_dir, filename)
        print(f"\nProcessing raw file: {filename}...")
        
        # 1. Load the raw OHLCV CSV file
        df = pd.read_csv(file_path)
        
        # 2. Data Cleaning & Feature Engineering
        # Ensure Date column is parsed as datetime and sorted
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
        
        # Calculate Daily Percentage Returns using 'Close' price
        df["Daily_Return"] = df["Close"].pct_change()
        
        # Calculate Moving Averages (e.g., 20-day and 50-day SMA for trend analysis)
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        
        # Calculate rolling average volume for liquidity / threshold filters
        df["Volume_SMA_20"] = df["Volume"].rolling(window=20).mean()
        
        # Drop rows with NaN values created by rolling windows/pct_change
        df_cleaned = df.dropna()
        
        # 3. Save processed data into data/processed/ folder
        processed_filename = filename.replace("_daily_", "_processed_")
        processed_path = os.path.join(processed_dir, processed_filename)
        
        df_cleaned.to_csv(processed_path, index=False)
        print(f"✅ Processed successfully! Saved to: {processed_path}")
        print(df_cleaned[["Date", "Close", "Daily_Return", "SMA_20","SMA_50","Volume_SMA_20"]].tail(2))

if __name__ == "__main__":
    process_raw_stock_data()

