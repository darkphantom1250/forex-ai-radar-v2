from app.database import (
    get_all_trades
)

# --------------------------------
# ANALYTICS ENGINE
# --------------------------------

def get_analytics():

    trades = get_all_trades()

    if not trades:

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

    closed = [

        trade for trade in trades

        if trade["trade_status"]
        in ["WIN", "LOSS"]
    ]

    total_trades = len(closed)

    wins = len([

        t for t in closed

        if t["trade_status"] == "WIN"
    ])

    losses = len([

        t for t in closed

        if t["trade_status"] == "LOSS"
    ])

    active_trades = len([

        t for t in trades

        if t["trade_status"] == "OPEN"
    ])

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

    rr_values = [

        float(t["rr"])

        for t in closed

        if t["rr"] is not None
    ]

    if rr_values:

        avg_rr = round(
            sum(rr_values)
            / len(rr_values),
            2
        )

    else:

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

    for trade in closed:

        pair = trade["pair"]

        if pair not in pair_stats:

            pair_stats[pair] = {

                "wins": 0,
                "total": 0
            }

        pair_stats[pair]["total"] += 1

        if trade["trade_status"] == "WIN":

            pair_stats[pair]["wins"] += 1

    best_pair = "-"

    best_rate = 0

    for pair, stats in pair_stats.items():

        if stats["total"] > 0:

            rate = (
                stats["wins"]
                / stats["total"]
            ) * 100

            if rate > best_rate:

                best_rate = rate

                best_pair = pair

    # --------------------------------
    # FINAL RESPONSE
    # --------------------------------

    return {

        "total_trades":
            total_trades,

        "wins":
            wins,

        "losses":
            losses,

        "win_rate":
            win_rate,

        "active_trades":
            active_trades,

        "profit_factor":
            profit_factor,

        "avg_rr":
            avg_rr,

        "best_pair":
            best_pair
    }