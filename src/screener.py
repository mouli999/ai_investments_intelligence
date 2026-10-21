import os
from datetime import datetime
import pandas as pd

def run_stock_screener():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, "data", "processed")
    
    if not os.path.exists(processed_dir):
        print("❌ Processed data directory not found.")
        return
        
    canonical_stock_files = [
        "HDFCBANK_NS_processed.csv",
        "INFY_NS_processed.csv",
        "RELIANCE_NS_processed.csv",
        "TCS_NS_processed.csv"
    ]
    
    qualified_stocks = []
    summary_data = []
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    print("🔍 Running Investment Screener (Clean Tickers & Neutral Trend Logic)...\n")
    print(f"{'Ticker':<14} | {'Close':<8} | {'SMA_20':<8} | {'SMA_50':<8} | {'20D Vol Avg':<12} | {'Trend Status'}")
    print("-" * 80)
    
    for filename in canonical_stock_files:
        file_path = os.path.join(processed_dir, filename)
        if not os.path.exists(file_path):
            continue
            
        df = pd.read_csv(file_path)
        if df.empty:
            continue
            
        ticker_name = filename.split('_processed')[0].upper().replace('_', '.')
        
        latest_row = df.iloc[-1]
        latest_close = latest_row["Close"]
        sma_20 = latest_row["SMA_20"]
        sma_50 = latest_row["SMA_50"]
        avg_volume_20 = latest_row["Volume_SMA_20"]
        
        is_liquid = avg_volume_20 > 100000
        
        # Trend separation: Bullish vs Bearish vs Neutral
        if latest_close > sma_20 and sma_20 > sma_50:
            trend_status = "BULLISH 🚀"
            is_bullish_trend = True
        elif latest_close < sma_20 and sma_20 < sma_50:
            trend_status = "BEARISH 📉"
            is_bullish_trend = False
        else:
            trend_status = "NEUTRAL / RANGE ⚖️"
            is_bullish_trend = False
            
        print(f"{ticker_name:<14} | {latest_close:<8.2f} | {sma_20:<8.2f} | {sma_50:<8.2f} | {avg_volume_20:<12,.0f} | {trend_status}")
        
        summary_data.append({
            "Ticker": ticker_name,
            "Date": date_str,
            "Latest_Close": latest_close,
            "SMA_20": sma_20,
            "SMA_50": sma_50,
            "Avg_Volume_20D": avg_volume_20,
            "Trend": trend_status,
            "Qualified": is_liquid and is_bullish_trend
        })
        
        if is_liquid and is_bullish_trend:
            qualified_stocks.append(ticker_name)
            
    print("\n" + "=" * 80)
    print(f"🎯 Screening Complete! Qualified stocks: {qualified_stocks}")
    
    reports_dir = os.path.join(project_root, "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"screener_report_{date_str}.csv")
    pd.DataFrame(summary_data).to_csv(report_path, index=False)
    print(f"📂 Report saved to: {report_path}")

if __name__ == "__main__":
    run_stock_screener()