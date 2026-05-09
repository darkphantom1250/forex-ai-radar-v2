import pandas as pd
import os

TRADE_FILE = "signals.csv"

# --------------------------------
# DIAGNOSTICS ENGINE
# --------------------------------

def get_diagnostics():

    if not os.path.exists(TRADE_FILE):

        return {
            "low_volatility": 0,
            "weak_candle": 0,
            "breakout_missing": 0,
            "htf_conflict": 0,
            "weak_setup": 0
        }

    try:

        df = pd.read_csv(TRADE_FILE)

    except Exception as e:

        print("DIAGNOSTICS ERROR:", e)

        return {
            "low_volatility": 0,
            "weak_candle": 0,
            "breakout_missing": 0,
            "htf_conflict": 0,
            "weak_setup": 0
        }

    if df.empty:

        return {
            "low_volatility": 0,
            "weak_candle": 0,
            "breakout_missing": 0,
            "htf_conflict": 0,
            "weak_setup": 0
        }

    # --------------------------------
    # COUNTERS
    # --------------------------------

    diagnostics = {
        "low_volatility": 0,
        "weak_candle": 0,
        "breakout_missing": 0,
        "htf_conflict": 0,
        "weak_setup": 0
    }

    # --------------------------------
    # SCAN REASONS
    # --------------------------------

    for _, row in df.iterrows():

        reason = str(
            row.get(
                "execution_reason",
                ""
            )
        ).lower()

        notes = str(
            row.get(
                "notes",
                ""
            )
        ).lower()

        combined = reason + " " + notes

        # LOW VOL
        if "low volatility" in combined:

            diagnostics[
                "low_volatility"
            ] += 1

        # WEAK CANDLE
        if "weak candle" in combined:

            diagnostics[
                "weak_candle"
            ] += 1

        # BREAKOUT
        if (
            "breakout" in combined
            and "no breakout" in combined
        ):

            diagnostics[
                "breakout_missing"
            ] += 1

        # HTF CONFLICT
        if (
            "conflict" in combined
            or "4h bearish" in combined
            or "4h bullish missing" in combined
        ):

            diagnostics[
                "htf_conflict"
            ] += 1

        # WEAK SETUP
        if "weak setup" in combined:

            diagnostics[
                "weak_setup"
            ] += 1

    return diagnostics