import ta


def add_indicators(df):

    # EMA
    df["ema50"] = ta.trend.ema_indicator(
        df["Close"],
        window=50
    )

    df["ema200"] = ta.trend.ema_indicator(
        df["Close"],
        window=200
    )

    # RSI
    df["rsi"] = ta.momentum.rsi(
        df["Close"],
        window=14
    )

    # ATR
    df["atr"] = ta.volatility.average_true_range(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=14
    )

    return df