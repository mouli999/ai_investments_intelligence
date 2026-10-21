import os
import pandas as pd

def run_stock_screener():
    processed_dir = os.path.join("data", "processed")
    
    if not os.path.exists(processed_dir):
        print("❌ Processed data directory not found. Please run Day 5 processing first.")
        return
        
    processed_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    
    if not processed_files:
        print("❌ No processed CSV files found in data/processed/.")
        return
        
    qualified_stocks = []
    
    print("🔍 Running Investment Screener across processed assets...\n")
    print(f"{'Ticker':<15} | {'Latest Close':<12} | {'20-Day Avg Vol':<15} | {'Trend Status'}")
    print("-" * 65)
    
    for filename in processed_files:
        file_path = os.path.join(processed_dir, filename)
        df = pd.read_csv(file_path)
        
        if df.empty:
            continue
            
        # Extract ticker symbol from filename (e.g., reliance_ns_processed_... -> RELIANCE.NS)
        ticker_name = filename.split('_processed_')[0].upper().replace('_', '.')
        
        # Get the most recent trading row (last row of the dataframe)
        latest_row = df.iloc[-1]
        
        latest_close = latest_row["Close"]
        avg_volume_20 = latest_row["Volume_SMA_20"]
        sma_20 = latest_row["SMA_20"]
        sma_50 = latest_row["SMA_50"]
        
        # Define screening criteria (e.g., Liquidity filter + Bullish Trend filter)
        # Criteria 1: Minimum average trading volume filter (e.g., > 100,000 shares)
        # Criteria 2: Close price above 20-day SMA (Short-term momentum)
        is_liquid = avg_volume_20 > 100000
        is_bullish_trend = latest_close > sma_20
        
        trend_status = "BULLISH 🚀" if is_bullish_trend else "BEARISH 📉"
        
        print(f"{ticker_name:<15} | {latest_close:<12.2f} | {avg_volume_20:<15,.0f} | {trend_status}")
        
        if is_liquid and is_bullish_trend:
            qualified_stocks.append(ticker_name)
            
    print("\n" + "=" * 65)
    print(f"🎯 Screening Complete! Qualified stocks passing liquidity & momentum filters: {qualified_stocks}")

if __name__ == "__main__":
    run_stock_screener()