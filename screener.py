import yfinance as yf
import pandas as pd
import time

def get_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    return tables[0]["Symbol"].tolist()

def screen_tickers(tickers):
    screened = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")
            if hist.empty or 'Volume' not in hist.columns:
                continue

            avg_volume = hist['Volume'][-10:].mean()
            current_price = hist['Close'].iloc[-1]
            high_60d = hist['Close'].max()

            if avg_volume > 10_000_000 and (current_price / high_60d) > 0.95:
                screened.append(ticker)

        except Exception as e:
            print(f"{ticker} failed: {e}")
        time.sleep(1.5)

    return screened

if __name__ == "__main__":
    tickers = get_tickers()
    screened = screen_tickers(tickers)
    if screened:
        pd.DataFrame(screened, columns=['Ticker']).to_csv('screened_tickers.csv', index=False)



