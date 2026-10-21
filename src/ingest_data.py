import os
import pandas as pd
from datetime import datetime
import yfinance as yf

def fetch_and_save_data():
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Watchlist including Nifty 50 benchmark + 4 core equities
    # Expanded period to 2 years (~500 trading days) to comfortably satisfy the 250-day lookback rule
    watchlist = ["^NSEI", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    
    for symbol in watchlist:
        print(f"\nFetching historical data for: {symbol}...")
        
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period="2y") # ~500 days to get >250 clean rows after warm-up
            
            if df.empty:
                print(f"❌ No data found for {symbol}.")
                continue
                
            # Reset index so 'Date' becomes a proper column
            df = df.reset_index()
            
            # Save raw data cleanly
            clean_ticker_name = symbol.replace("^", "").replace(".", "_")
            filename = f"{clean_ticker_name}_raw_{date_str}.csv"
            file_path = os.path.join(raw_dir, filename)
            
            df.to_csv(file_path, index=False)
            print(f"✅ Success! Saved to: {file_path} ({len(df)} rows)")
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

if __name__ == "__main__":
    fetch_and_save_data()