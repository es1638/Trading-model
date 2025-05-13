import yfinance as yf
import pandas as pd
import time

def get_tickers():
    print("🔍 Fetching S&P 500 ticker list...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    tickers = tables[0]["Symbol"].tolist()
    print(f"✅ Retrieved {len(tickers)} tickers.")
    return tickers

def screen_tickers(tickers):
    screened = []
    print("📊 Screening tickers... (with delays to avoid rate limits)")
    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")
            if hist.empty or 'Volume' not in hist.columns:
                continue

            avg_volume = hist['Volume'][-10:].mean()
            current_price = hist['Close'].iloc[-1]

            info = stock.info
            beta = info.get('beta', None)
            high_52w = info.get('fiftyTwoWeekHigh', None)

            if (
                avg_volume > 10_000_000 and
                beta is not None and beta > 1 and
                high_52w is not None and
                (current_price / high_52w) > 0.95
            ):
                screened.append(ticker)

            print(f"✅ {ticker} passed screening. ({len(screened)} total)")

        except Exception as e:
            print(f"❌ {ticker}: {e}")

        # 🔁 Add a delay after each request to avoid getting blocked
        time.sleep(1.5)

    print(f"✅ Screening complete: {len(screened)} tickers passed.")
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


