import yfinance as yf
import pandas as pd

def get_tickers():
    print("🔍 Fetching S&P 500 ticker list from Wikipedia...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    tickers = tables[0]["Symbol"].tolist()
    print(f"✅ Retrieved {len(tickers)} tickers.")
    return tickers

def screen_tickers(tickers):
    screened = []
    print("📊 Screening tickers...")
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")

            if hist.empty or 'Volume' not in hist.columns:
                continue

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
        except Exception as e:
            print(f"❌ Failed on {ticker}: {e}")
            continue

    print(f"✅ {len(screened)} tickers passed screening.")
    return screened

if __name__ == "__main__":
    try:
        tickers = get_tickers()
        screened = screen_tickers(tickers)
        if screened:
            pd.DataFrame(screened, columns=['Ticker']).to_csv('screened_tickers.csv', index=False)
            print("📁 screened_tickers.csv created successfully.")
        else:
            print("⚠️ No tickers passed screening.")
    except Exception as e:
        print(f"🚨 screener.py failed: {e}")

