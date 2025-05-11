import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_tickers():
    sp500 = pd.read_csv('sp500_tickers.csv')  # Add this file manually
    return sp500['Symbol'].tolist()

def screen_tickers(tickers):
    screened = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")
            avg_volume = hist['Volume'][-10:].mean()
            beta = stock.info.get('beta', 0)
            current_price = hist['Close'].iloc[-1]
            high_52w = stock.info.get('fiftyTwoWeekHigh', None)

            if (
                avg_volume > 10_000_000 and
                beta is not None and beta > 1 and
                high_52w is not None and
                (current_price / high_52w) > 0.95
            ):
                screened.append(ticker)
        except Exception:
            continue

    return screened

if __name__ == "__main__":
    tickers = get_tickers()
    screened = screen_tickers(tickers)
    pd.DataFrame(screened, columns=['Ticker']).to_csv('screened_tickers.csv', index=False)
    print(f"Screened {len(screened)} tickers saved to screened_tickers.csv")