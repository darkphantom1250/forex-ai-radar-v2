import pandas as pd
import os

TRADE_FILE = "signals.csv"

# --------------------------------
# ANALYTICS ENGINE
# --------------------------------

def get_analytics():

    # --------------------------------
    # NO FILE
    # --------------------------------

    if not os.path.exists(TRADE_FILE):

        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "active_trades": 0,
            "profit_factor": 0,
            "avg_rr": 0,
            "best_pair": "-"
        }

    # --------------------------------
    # LOAD CSV
    # --------------------------------

    try:

        df = pd.read_csv(TRADE_FILE)

    except Exception as e:

        print("ANALYTICS CSV ERROR:", e)

        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "active_trades": 0,
            "profit_factor": 0,
            "avg_rr": 0,
            "best_pair": "-"
        }

    # --------------------------------
    # EMPTY
    # --------------------------------

    if df.empty:

        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "active_trades": 0,
            "profit_factor": 0,
            "avg_rr": 0,
            "best_pair": "-"
        }

    # --------------------------------
    # CLOSED TRADES
    # --------------------------------

    closed = df[
        df["trade_status"].isin(
            ["WIN", "LOSS"]
        )
    ]

    total_trades = len(closed)

    wins = len(
        closed[
            closed["trade_status"] == "WIN"
        ]
    )

    losses = len(
        closed[
            closed["trade_status"] == "LOSS"
        ]
    )

    active_trades = len(
        df[
            df["trade_status"] == "OPEN"
        ]
    )

    # --------------------------------
    # WIN RATE
    # --------------------------------

    if total_trades > 0:

        win_rate = round(
            (wins / total_trades) * 100,
            2
        )

    else:

        win_rate = 0

    # --------------------------------
    # AVG RR
    # --------------------------------

    avg_rr = 0

    if "rr" in closed.columns:

        rr_values = (
            closed["rr"]
            .dropna()
        )

        if not rr_values.empty:

            try:

                avg_rr = round(
                    float(
                        rr_values.mean()
                    ),
                    2
                )

            except Exception:

                avg_rr = 0

    # --------------------------------
    # PROFIT FACTOR
    # --------------------------------

    gross_profit = wins * avg_rr
    gross_loss = losses * 1

    if gross_loss > 0:

        profit_factor = round(
            gross_profit / gross_loss,
            2
        )

    else:

        profit_factor = 0

    # --------------------------------
    # BEST PAIR
    # --------------------------------

    pair_stats = {}

    if not closed.empty:

        for pair in closed["pair"].unique():

            pair_df = closed[
                closed["pair"] == pair
            ]

            pair_wins = len(
                pair_df[
                    pair_df["trade_status"] == "WIN"
                ]
            )

            pair_total = len(pair_df)

            if pair_total > 0:

                pair_stats[pair] = round(
                    (pair_wins / pair_total) * 100,
                    2
                )

    best_pair = "-"

    if pair_stats:

        best_pair = max(
            pair_stats,
            key=pair_stats.get
        )

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return {

        "total_trades": int(total_trades),

        "wins": int(wins),

        "losses": int(losses),

        "win_rate": float(win_rate),

        "active_trades": int(active_trades),

        "profit_factor": float(profit_factor),

        "avg_rr": float(avg_rr),

        "best_pair": best_pair
    }