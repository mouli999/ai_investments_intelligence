import os
import pandas as pd
from datetime import datetime
import yfinance as yf




def fetch_and_save_indian_stocks(tickers):

    raw_dir=os.path.join("data","raw")
    os.makedirs(raw_dir,exist_ok=True)

    date_str=datetime.now().strftime("%Y-%m-%d")

    for symbol in tickers:
        print(f"\n Fetching historical data for Indian stock: {symbol}...")

        try:
            stock=yf.Ticker(symbol)
            df=stock.history(period='6mo')

            if df.empty:
                print(f"no data found for {symbol}. Check if the ticker symbol is correct.")
                continue

            # save the raw_data as csv or json inside data/raw/
            # csv is standard for tabular OHLCV data

            filename= f"{symbol.replace('.','_')}_dly_{date_str}.csv"
            file_path=os.path.join(raw_dir,filename)

            df.to_csv(file_path)
            print(f" Success! Raw data saved to {file_path}")
            print(df.tail(2))

        except Exception:
            print(f"Error fetching {symbol} : {Exception}")

if __name__=="__main__":
    indian_watchlist=["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]
    fetch_and_save_indian_stocks(indian_watchlist)
