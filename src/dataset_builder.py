import os
import pandas as pd

def build_point_in_time_dataset():
    processed_dir = os.path.join("data", "processed")
    dataset_dir = os.path.join("data", "ml_ready")
    os.makedirs(dataset_dir, exist_ok=True)
    
    if not os.path.exists(processed_dir):
        print("❌ Processed data directory not found. Run Day 5 processing first.")
        return
        
    processed_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    
    all_stock_data = []
    
    print("⚙️ Constructing Point-in-Time features & T+11 to T+15 Outperformance Targets...\n")
    
    for filename in processed_files:
        file_path = os.path.join(processed_dir, filename)
        df = pd.read_csv(file_path)
        
        if df.empty:
            continue
            
        clean_name = filename.split('_processed_')[0].split('.dly')[0].split('.csv')[0]
        ticker_name = clean_name.upper().replace('_', '.')
        
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        
        # --- FORWARD EVALUATION WINDOW: T+11 to T+15 ---
        # Calculate daily returns first if not present
        if "Daily_Return" not in df.columns:
            df["Daily_Return"] = df["Close"].pct_change()
            
        # To evaluate the window from T+11 to T+15:
        # We can calculate the mean return across t+11, t+12, t+13, t+14, t+15.
        # In pandas, rolling mean of future values can be achieved by reversing or shifting.
        # Alternatively, find the average price over T+11 to T+15 relative to T.
        
        # Let's compute average return across the T+11 to T+15 window:
        # We shift backward so that row T contains the mean return from index T+11 to T+15.
        # A clean way is taking the rolling mean of Daily_Return shifted backwards.
        
        # Mean return of the stock from T+11 to T+15:
        # We can average the 'Daily_Return' values from shift(-11) to shift(-15)
        future_window_returns = pd.concat([df["Daily_Return"].shift(-i) for i in range(11, 16)], axis=1).mean(axis=1)
        df["Stock_Avg_Return_T11_T15"] = future_window_returns
        
        # Note: In a complete pipeline, we will also bring in the Nifty 50 benchmark return for T+11 to T+15.
        # For now, let's set a placeholder or baseline benchmark assumption (e.g., assuming 0% or matching benchmark file)
        # Let's assume Benchmark Return for T+11 to T+15 is fetched or defaulted to 0 for single-stock testing:
        benchmark_return_placeholder = 0.00  # Will be replaced by actual Nifty 50 index data file later
        
        buffer_threshold = 0.055  # 5.5% outperformance buffer (5.0% target + 0.5% taxes/slippage)
        
        # Ground Truth Label (y) calculation from problem statement:
        # Stock Average Return (T+11 to T+15) >= [Benchmark Average Return + 5.5%]
        df["Target"] = (df["Stock_Avg_Return_T11_T15"] >= (benchmark_return_placeholder + buffer_threshold)).astype(int)
        
        df["Ticker"] = ticker_name
        
        # Drop rows where future evaluation window goes beyond available data (the last 15 rows)
        df_ml = df.dropna(subset=["Stock_Avg_Return_T11_T15", "SMA_50"]).copy()
        
        cols_to_keep = ["Date", "Ticker", "Close", "SMA_20", "SMA_50", "Volume_SMA_20", "Stock_Avg_Return_T11_T15", "Target"]
        df_ml = df_ml[cols_to_keep]
        
        all_stock_data.append(df_ml)
        
    if all_stock_data:
        master_df = pd.concat(all_stock_data, ignore_index=True)
        dataset_path = os.path.join(dataset_dir, "point_in_time_features_targets.csv")
        master_df.to_csv(dataset_path, index=False)
        
        print(f"✅ Point-in-Time dataset successfully aligned with Problem Statement (T+11 to T+15 window)!")
        print(f"📂 Saved to: {dataset_path}")
        print("\n--- Sample Snapshot ---")
        print(master_df[["Date", "Ticker", "Close", "Stock_Avg_Return_T11_T15", "Target"]].tail(3))
    else:
        print("❌ No data available.")

if __name__ == "__main__":
    build_point_in_time_dataset()
    
    