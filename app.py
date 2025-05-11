import streamlit as st
import pandas as pd
import lightgbm as lgb
import yfinance as yf
import time
import subprocess
import os
from datetime import datetime
import pytz
from utils.feature_engineering import generate_features

MODEL_PATH = 'lightgbm_model.txt'
THRESHOLD = 0.9761

def run_screener_if_morning():
    est = pytz.timezone('US/Eastern')
    now_est = datetime.now(est)
    if now_est.hour < 9 or (now_est.hour == 9 and now_est.minute < 30):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime("screened_tickers.csv"), est)
            if file_time.date() < now_est.date():
                subprocess.run(["python", "screener.py"])
        except FileNotFoundError:
            subprocess.run(["python", "screener.py"])

@st.cache_resource
def load_model():
    model = lgb.Booster(model_file=MODEL_PATH)
    return model

def fetch_prev_close(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        return hist['Close'].iloc[-2]
    except:
        return None

def fetch_intraday_data(ticker):
    try:
        return yf.download(ticker, period="1d", interval="1m", progress=False)
    except:
        return None

def main():
    st.set_page_config(layout="centered", page_title="Live Stock Predictor")
    st.title("📈 Live 30-Minute Breakout Predictor")
    st.caption(f"Model threshold: {THRESHOLD} | Updated every 2 minutes")

    run_screener_if_morning()
    model = load_model()

    try:
        tickers = pd.read_csv('screened_tickers.csv')['Ticker'].tolist()
    except FileNotFoundError:
        st.error("screened_tickers.csv not found and screener.py failed to create it.")
        return

    signal_list = []
    with st.spinner("Fetching and evaluating live data..."):
        for ticker in tickers:
            prev_close = fetch_prev_close(ticker)
            if prev_close is None:
                continue

            intraday_df = fetch_intraday_data(ticker)
            if intraday_df is None or len(intraday_df) < 15:
                continue

            features = generate_features(intraday_df, prev_close=prev_close)
            if features is None:
                continue

            pred_prob = model.predict(features)[0]
            if pred_prob > THRESHOLD:
                signal_list.append((ticker, round(pred_prob, 4)))

    if signal_list:
        st.success("### ✅ Buy Signals")
        for ticker, prob in sorted(signal_list, key=lambda x: -x[1]):
            st.write(f"- {ticker}: **{prob}**")
    else:
        st.warning("⚠️ No breakout signals at this time.")

    st.markdown(f"**Last refreshed:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.experimental_rerun() if st.button("🔄 Refresh Now") else time.sleep(120) or st.experimental_rerun()

if __name__ == "__main__":
    main()