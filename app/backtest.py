import yfinance as yf
import pandas as pd

from app.indicators import add_indicators
from app.scanner import analyze_market, get_trend


PAIR = "EURUSD=X"


def run_backtest():

    wins = 0
    losses = 0
    total_trades = 0

    total_rr = 0

    # --------------------------------
    # LOAD 15m DATA
    # --------------------------------

    df_15m = yf.download(
        PAIR,
        period="60d",
        interval="15m",
        auto_adjust=True,
        progress=False
    )

    df_15m.columns = df_15m.columns.get_level_values(0)

    df_15m = add_indicators(df_15m)

    # --------------------------------
    # LOAD 4H DATA
    # --------------------------------

    df_4h = yf.download(
        PAIR,
        period="180d",
        interval="4h",
        auto_adjust=True,
        progress=False
    )

    df_4h.columns = df_4h.columns.get_level_values(0)

    df_4h = add_indicators(df_4h)

    # --------------------------------
    # MAIN LOOP
    # --------------------------------

    for i in range(250, len(df_15m) - 20):

        row = df_15m.iloc[i]

        current_time = df_15m.index[i]

        # --------------------------------
        # DYNAMIC 4H FILTER
        # --------------------------------

        historical_4h = df_4h[df_4h.index <= current_time]

        if len(historical_4h) < 200:
            continue

        higher_trend = get_trend(historical_4h)

        # --------------------------------
        # BREAKOUT LEVELS
        # --------------------------------

        breakout_high = (
            df_15m["High"]
            .iloc[i-20:i]
            .max()
        )

        breakout_low = (
            df_15m["Low"]
            .iloc[i-20:i]
            .min()
        )

        # --------------------------------
        # ANALYSIS
        # --------------------------------

        analysis = analyze_market(
            row,
            higher_trend,
            breakout_high,
            breakout_low
        )

        signal = analysis["signal"]

        if signal not in [
            "WEAK BUY",
            "STRONG BUY",
            "WEAK SELL",
            "STRONG SELL"
        ]:
            continue

        entry = row["Close"]

        sl = analysis["sl"]
        tp = analysis["tp"]

        rr = analysis["rr"]

        if not sl or not tp:
            continue

        total_trades += 1

        # --------------------------------
        # FUTURE CANDLE SIMULATION
        # --------------------------------

        future_data = df_15m.iloc[i+1:i+20]

        trade_result = None

        for _, candle in future_data.iterrows():

            high = candle["High"]
            low = candle["Low"]

            # BUY LOGIC
            if "BUY" in signal:

                if low <= sl:
                    trade_result = "LOSS"
                    break

                if high >= tp:
                    trade_result = "WIN"
                    break

            # SELL LOGIC
            elif "SELL" in signal:

                if high >= sl:
                    trade_result = "LOSS"
                    break

                if low <= tp:
                    trade_result = "WIN"
                    break

        # --------------------------------
        # STORE RESULTS
        # --------------------------------

        if trade_result == "WIN":
            wins += 1
            total_rr += rr

        elif trade_result == "LOSS":
            losses += 1
            total_rr -= 1

    # --------------------------------
    # FINAL METRICS
    # --------------------------------

    win_rate = 0

    if total_trades > 0:
        win_rate = (wins / total_trades) * 100

    print("\n========== BACKTEST RESULTS ==========")

    print(f"Pair: {PAIR}")

    print(f"Total Trades: {total_trades}")

    print(f"Wins: {wins}")

    print(f"Losses: {losses}")

    print(f"Win Rate: {round(win_rate, 2)}%")

    print(f"Total RR: {round(total_rr, 2)}")

    print("======================================\n")


if __name__ == "__main__":
    run_backtest()