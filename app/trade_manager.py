import yfinance as yf

from app.database import (
    get_open_trades,
    update_trade_status
)

# --------------------------------
# UPDATE TRADE STATUS
# --------------------------------

def manage_trades():

    trades = get_open_trades()

    if not trades:

        print("NO OPEN TRADES")

        return

    for row in trades:

        signal = row["signal"]

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

            high = float(
                latest["High"]
            )

            low = float(
                latest["Low"]
            )

            tp = float(
                row["tp"]
            )

            sl = float(
                row["sl"]
            )

            # --------------------------------
            # BUY TRADE
            # --------------------------------

            if signal == "BUY":

                if high >= tp:

                    update_trade_status(
                        row["signal_id"],
                        "WIN"
                    )

                    print(
                        f"{pair} BUY WIN"
                    )

                elif low <= sl:

                    update_trade_status(
                        row["signal_id"],
                        "LOSS"
                    )

                    print(
                        f"{pair} BUY LOSS"
                    )

            # --------------------------------
            # SELL TRADE
            # --------------------------------

            elif signal == "SELL":

                if low <= tp:

                    update_trade_status(
                        row["signal_id"],
                        "WIN"
                    )

                    print(
                        f"{pair} SELL WIN"
                    )

                elif high >= sl:

                    update_trade_status(
                        row["signal_id"],
                        "LOSS"
                    )

                    print(
                        f"{pair} SELL LOSS"
                    )

        except Exception as e:

            print(
                f"{pair} TRADE ERROR:",
                e
            )