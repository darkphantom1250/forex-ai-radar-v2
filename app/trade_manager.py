import pandas as pd
import yfinance as yf
import os

CSV_FILE = "signals.csv"

def update_trade_status():

    if not os.path.exists(CSV_FILE):

       print("signals.csv missing")

       return


    try:

        df = pd.read_csv(CSV_FILE)

    except Exception as e:

        print("CSV READ ERROR:", e)
        return

    if df.empty:
        return

    updated = False

    for i, row in df.iterrows():

        # -----------------------
        # ONLY OPEN TRADES
        # -----------------------

        if row["trade_status"] != "OPEN":
            continue

        signal = row["signal"]

        # -----------------------
        # IGNORE WAIT SIGNALS
        # -----------------------

        if signal == "WAIT":
            continue

        pair = row["pair"]

        try:

            data = yf.download(
                pair,
                period="1d",
                interval="15m",
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                continue

            data.columns = (
                data.columns
                .get_level_values(0)
            )

            latest = data.iloc[-1]

            high = float(latest["High"])
            low = float(latest["Low"])

            tp = float(row["tp"])
            sl = float(row["sl"])

            # -----------------------
            # BUY TRADE
            # -----------------------

            if signal == "BUY":

                if high >= tp:

                    df.at[i, "trade_status"] = "WIN"

                    print(
                        f"{pair} BUY WIN"
                    )

                    updated = True

                elif low <= sl:

                    df.at[i, "trade_status"] = "LOSS"

                    print(
                        f"{pair} BUY LOSS"
                    )

                    updated = True

            # -----------------------
            # SELL TRADE
            # -----------------------

            elif signal == "SELL":

                if low <= tp:

                    df.at[i, "trade_status"] = "WIN"

                    print(
                        f"{pair} SELL WIN"
                    )

                    updated = True

                elif high >= sl:

                    df.at[i, "trade_status"] = "LOSS"

                    print(
                        f"{pair} SELL LOSS"
                    )

                    updated = True

        except Exception as e:

            print(
                f"{pair} TRADE ERROR:",
                e
            )

    # -----------------------
    # SAVE CSV
    # -----------------------

    if updated:

        df.to_csv(
            CSV_FILE,
            index=False
        )

        print(
            "TRADE STATUS UPDATED"
        )