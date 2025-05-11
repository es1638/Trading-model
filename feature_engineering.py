import pandas as pd
import numpy as np

def generate_features(df, prev_close=None):
    try:
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        if prev_close is None:
            prev_close = df['Open'].iloc[0]

        df['change_from_prev_close'] = (df['Close'] - prev_close) / prev_close
        df['return_5'] = df['Close'].pct_change(5)
        df['return_10'] = df['Close'].pct_change(10)
        df['return_15'] = df['Close'].pct_change(15)
        df['volatility_10'] = df['Close'].pct_change().rolling(10).std()
        df['volatility_20'] = df['Close'].pct_change().rolling(20).std()
        df['rolling_volume_5'] = df['Volume'].rolling(5).mean()
        df['rolling_volume_10'] = df['Volume'].rolling(10).mean()
        df['high_from_prev_close'] = (df['High'] - prev_close) / prev_close
        df['low_from_prev_close'] = (df['Low'] - prev_close) / prev_close
        df['open_close_spread'] = (df['Open'] - df['Close']) / df['Open']
        df['momentum_10'] = df['Close'] / df['Close'].rolling(10).mean()

        df = df.dropna()

        feature_columns = [
            'change_from_prev_close',
            'return_5', 'return_10', 'return_15',
            'volatility_10', 'volatility_20',
            'rolling_volume_5', 'rolling_volume_10',
            'high_from_prev_close', 'low_from_prev_close',
            'open_close_spread', 'momentum_10'
        ]

        return df[feature_columns].iloc[[-1]]

    except Exception as e:
        print(f"Feature generation failed: {e}")
        return None