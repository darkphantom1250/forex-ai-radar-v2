import yfinance as yf
import pandas as pd
import ta
import csv
import os
import uuid
import requests

from datetime import datetime, timezone

# --------------------------------
# ENV VARIABLES
# --------------------------------

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

# --------------------------------
# PAIRS
# --------------------------------

PAIRS = [
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X"
]

# --------------------------------
# MARKET SESSION
# --------------------------------

def get_market_session():

    hour = datetime.utcnow().hour

    if 0 <= hour < 7:
        return "ASIA"

    elif 7 <= hour < 13:
        return "LONDON"

    elif 13 <= hour < 21:
        return "NEW_YORK"

    return "OFF_HOURS"

# --------------------------------
# TELEGRAM ALERT
# --------------------------------

def send_telegram_alert(signal):

    if (
        not TELEGRAM_BOT_TOKEN
        or not TELEGRAM_CHAT_ID
    ):
        return

    try:

        message = f"""
🚨 Forex AI Radar Alert

Pair: {signal['pair']}

Signal: {signal['signal']}

Bias: {signal['bias']}

Quality: {signal['setup_quality']}

Score: {signal['setup_score']}

Entry: {signal['entry_price']}

SL: {signal['sl']}

TP: {signal['tp']}

RR: {signal['rr']}

Reason: {signal['execution_reason']}
"""

        url = (
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        requests.post(
            url,
            data=payload,
            timeout=10
        )

        print(
            f"TELEGRAM SENT: "
            f"{signal['pair']} "
            f"{signal['signal']}"
        )

    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            e
        )

# --------------------------------
# SCAN MARKETS
# --------------------------------

def scan_markets():

    results = []

    # --------------------------------
    # CSV SETUP
    # --------------------------------

    file_exists = os.path.isfile(
        "signals.csv"
    )

    with open(
        "signals.csv",
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # --------------------------------
        # HEADERS
        # --------------------------------

        if not file_exists:

            writer.writerow([

                "signal_id",

                "timestamp",

                "pair",

                "signal",

                "bias",

                "setup_quality",

                "setup_score",

                "market_session",

                "rsi",

                "atr_percent",

                "candle_strength",

                "execution_ready",

                "execution_reason",

                "notes",

                "reasons",

                "entry_price",

                "sl",

                "tp",

                "rr",

                "trade_status"
            ])

        # --------------------------------
        # LOOP PAIRS
        # --------------------------------

        for pair in PAIRS:

            try:

                # --------------------------------
                # DOWNLOAD DATA
                # --------------------------------

                df_15m = yf.download(
                    pair,
                    period="5d",
                    interval="15m",
                    auto_adjust=True,
                    progress=False
                )

                df_4h = yf.download(
                    pair,
                    period="30d",
                    interval="4h",
                    auto_adjust=True,
                    progress=False
                )

                if (
                    df_15m.empty
                    or df_4h.empty
                ):
                    continue

                # flatten columns
                df_15m.columns = (
                    df_15m.columns
                    .get_level_values(0)
                )

                df_4h.columns = (
                    df_4h.columns
                    .get_level_values(0)
                )

                # --------------------------------
                # INDICATORS
                # --------------------------------

                df_15m["ema20"] = ta.trend.ema_indicator(
                    df_15m["Close"],
                    window=20
                )

                df_15m["ema50"] = ta.trend.ema_indicator(
                    df_15m["Close"],
                    window=50
                )

                df_15m["rsi"] = ta.momentum.rsi(
                    df_15m["Close"],
                    window=14
                )

                atr = ta.volatility.average_true_range(
                    df_15m["High"],
                    df_15m["Low"],
                    df_15m["Close"],
                    window=14
                )

                df_15m["atr"] = atr

                df_4h["ema20"] = ta.trend.ema_indicator(
                    df_4h["Close"],
                    window=20
                )

                df_4h["ema50"] = ta.trend.ema_indicator(
                    df_4h["Close"],
                    window=50
                )

                latest_15m = df_15m.iloc[-1]
                latest_4h = df_4h.iloc[-1]

                close = float(
                    latest_15m["Close"]
                )

                rsi = round(
                    float(latest_15m["rsi"]),
                    2
                )

                atr_value = float(
                    latest_15m["atr"]
                )

                atr_percent = round(
                    atr_value / close,
                    6
                )

                # --------------------------------
                # TREND
                # --------------------------------

                bullish_15m = (
                    latest_15m["ema20"]
                    >
                    latest_15m["ema50"]
                )

                bullish_4h = (
                    latest_4h["ema20"]
                    >
                    latest_4h["ema50"]
                )

                bearish_15m = (
                    latest_15m["ema20"]
                    <
                    latest_15m["ema50"]
                )

                bearish_4h = (
                    latest_4h["ema20"]
                    <
                    latest_4h["ema50"]
                )

                # --------------------------------
                # SIGNAL
                # --------------------------------

                signal = "WAIT"
                bias = "NEUTRAL"

                if bullish_15m:
                    bias = "BULLISH"

                elif bearish_15m:
                    bias = "BEARISH"

                # --------------------------------
                # SCORE SYSTEM
                # --------------------------------

                setup_score = 0

                reasons = []

                execution_reason = ""

                # HTF ALIGNMENT

                if bullish_15m and bullish_4h:

                    setup_score += 25

                    reasons.append(
                        "15m bullish trend"
                    )

                    reasons.append(
                        "4H bullish confirmation"
                    )

                elif bearish_15m and bearish_4h:

                    setup_score += 25

                    reasons.append(
                        "15m bearish trend"
                    )

                    reasons.append(
                        "4H bearish confirmation"
                    )

                else:

                    reasons.append(
                        "HTF conflict"
                    )

                # RSI

                if bullish_15m and rsi > 52:

                    setup_score += 15

                    reasons.append(
                        "Bullish RSI momentum"
                    )

                elif bearish_15m and rsi < 48:

                    setup_score += 15

                    reasons.append(
                        "Bearish RSI momentum"
                    )

                else:

                    reasons.append(
                        "Weak RSI"
                    )

                # CANDLE STRENGTH

                candle_body = abs(
                    latest_15m["Close"]
                    -
                    latest_15m["Open"]
                )

                candle_range = (
                    latest_15m["High"]
                    -
                    latest_15m["Low"]
                )

                candle_strength = 0

                if candle_range > 0:

                    candle_strength = round(
                        candle_body
                        /
                        candle_range,
                        2
                    )

                if candle_strength > 0.55:

                    setup_score += 20

                    reasons.append(
                        "Strong candle"
                    )

                else:

                    reasons.append(
                        "Weak candle"
                    )

                # VOLATILITY

                if atr_percent > 0.00035:

                    setup_score += 20

                    reasons.append(
                        "Healthy volatility"
                    )

                else:

                    reasons.append(
                        "Low volatility"
                    )

                # BREAKOUT

                recent_high = (
                    df_15m["High"]
                    .tail(10)
                    .max()
                )

                recent_low = (
                    df_15m["Low"]
                    .tail(10)
                    .min()
                )

                breakout = False

                if (
                    bullish_15m
                    and close >= recent_high
                ):

                    breakout = True

                    setup_score += 20

                    reasons.append(
                        "Bullish breakout"
                    )

                elif (
                    bearish_15m
                    and close <= recent_low
                ):

                    breakout = True

                    setup_score += 20

                    reasons.append(
                        "Bearish breakout"
                    )

                else:

                    reasons.append(
                        "No breakout yet"
                    )

                # QUALITY

                if setup_score >= 80:

                    setup_quality = "HIGH"

                elif setup_score >= 55:

                    setup_quality = "MEDIUM"

                else:

                    setup_quality = "LOW"

                # EXECUTION

                execution_ready = False

                if (
                    setup_score >= 80
                    and breakout
                    and candle_strength > 0.55
                ):

                    execution_ready = True

                    execution_reason = (
                        "Conditions aligned"
                    )

                else:

                    if not breakout:

                        execution_reason = (
                            "Breakout missing"
                        )

                    elif candle_strength <= 0.55:

                        execution_reason = (
                            "Weak candle"
                        )

                    elif atr_percent <= 0.00035:

                        execution_reason = (
                            "Low volatility"
                        )

                    else:

                        execution_reason = (
                            "Weak setup"
                        )

                # FINAL SIGNAL

                if execution_ready:

                    if bullish_15m:

                        signal = "BUY"

                    elif bearish_15m:

                        signal = "SELL"

                # RR

                rr = 2.0

                sl_distance = atr_value * 1.5

                if bullish_15m:

                    sl = round(
                        close - sl_distance,
                        5
                    )

                    tp = round(
                        close + (
                            sl_distance * rr
                        ),
                        5
                    )

                else:

                    sl = round(
                        close + sl_distance,
                        5
                    )

                    tp = round(
                        close - (
                            sl_distance * rr
                        ),
                        5
                    )

                # SESSION

                market_session = (
                    get_market_session()
                )

                # RESULT

                result = {

                    "pair": pair,

                    "signal": signal,

                    "bias": bias,

                    "setup_quality":
                        setup_quality,

                    "setup_score":
                        setup_score,

                    "market_session":
                        market_session,

                    "rsi": rsi,

                    "atr_percent":
                        atr_percent,

                    "candle_strength":
                        candle_strength,

                    "execution_ready":
                        execution_ready,

                    "execution_reason":
                        execution_reason,

                    "reasons": reasons,

                    "entry_price":
                        round(close, 5),

                    "sl": sl,

                    "tp": tp,

                    "rr": rr
                }

                results.append(result)

                # TELEGRAM ONLY FOR REAL TRADES

                if signal in ["BUY", "SELL"]:

                    send_telegram_alert(
                        result
                    )

                # CSV LOGGING

                writer.writerow([

                    str(uuid.uuid4())[:8],

                    datetime.now(
                        timezone.utc
                    ).isoformat(),

                    pair,

                    signal,

                    bias,

                    setup_quality,

                    setup_score,

                    market_session,

                    rsi,

                    atr_percent,

                    candle_strength,

                    execution_ready,

                    execution_reason,

                    "|".join(reasons),

                    "|".join(reasons),

                    round(close, 5),

                    sl,

                    tp,

                    rr,

                    "OPEN"
                ])

            except Exception as e:

                print(
                    f"{pair} ERROR:",
                    e
                )

    return results