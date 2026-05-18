import pandas as pd
import numpy as np

def add_indicators(df):

    # EMA
    df['EMA20'] = df['Close'].ewm(span=20).mean()

    df['EMA50'] = df['Close'].ewm(span=50).mean()

    # RSI
    delta = df['Close'].diff()

    gain = delta.where(delta > 0, 0)

    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(alpha=1/14).mean()

    avg_loss = loss.ewm(alpha=1/14).mean()

    rs = avg_gain / avg_loss

    df['RSI'] = 100 - (100 / (1 + rs))

    # VWAP
    tp = (
        df['High'] +
        df['Low'] +
        df['Close']
    ) / 3

    df['VWAP'] = (
        (tp * df['Volume']).cumsum()
        / df['Volume'].cumsum()
    )

    # ATR
    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift()),
            abs(df['Low'] - df['Close'].shift())
        )
    )

    df['ATR'] = df['TR'].rolling(14).mean()

    df.dropna(inplace=True)

    return df
