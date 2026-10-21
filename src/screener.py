import os
from datetime import datetime
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
    summary_data = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("🔍 Running Investment Screener across processed assets (with SMA-50 & Volumes)...\n")
    print(f"{'Ticker':<14} | {'Close':<8} | {'SMA_20':<8} | {'SMA_50':<8} | {'20D Vol Avg':<12} | {'Trend'}")
    print("-" * 80)
    
    for filename in processed_files:
        file_path = os.path.join(processed_dir, filename)
        df = pd.read_csv(file_path)
        
        if df.empty:
            continue
            
        # Cleanly extract the ticker name
        base_name = filename.split('_processed_')[0]
        ticker_name = base_name.upper().replace('_', '.')
        
        # Get the most recent trading row
        latest_row = df.iloc[-1]
        
        latest_close = latest_row["Close"]
        sma_20 = latest_row["SMA_20"]
        sma_50 = latest_row["SMA_50"]
        avg_volume_20 = latest_row["Volume_SMA_20"]
        
        # Screening criteria
        is_liquid = avg_volume_20 > 100000
        is_bullish_trend = latest_close > sma_20 and sma_20 > sma_50  # Golden/Bullish structure check
        
        trend_status = "BULLISH 🚀" if is_bullish_trend else "BEARISH 📉"
        
        print(f"{ticker_name:<14} | {latest_close:<8.2f} | {sma_20:<8.2f} | {sma_50:<8.2f} | {avg_volume_20:<12,.0f} | {trend_status}")
        
        # Track full details for the permanent report
        summary_data.append({
            "Ticker": ticker_name,
            "Date": date_str,
            "Latest_Close": latest_close,
            "SMA_20": sma_20,
            "SMA_50": sma_50,
            "Avg_Volume_20D": avg_volume_20,
            "Trend": "Bullish" if is_bullish_trend else "Bearish",
            "Qualified": is_liquid and is_bullish_trend
        })
        
        if is_liquid and is_bullish_trend:
            qualified_stocks.append(ticker_name)
            
    print("\n" + "=" * 80)
    print(f"🎯 Screening Complete! Qualified stocks: {qualified_stocks}")
    
    # Save the expanded report to data/reports/
    reports_dir = os.path.join("data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_path = os.path.join(reports_dir, f"screener_report_{date_str}.csv")
    report_df = pd.DataFrame(summary_data)
    report_df.to_csv(report_path, index=False)
    print(f"📂 Updated permanent screening report saved to: {report_path}")

if __name__ == "__main__":
    run_stock_screener()