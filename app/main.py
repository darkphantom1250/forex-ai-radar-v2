from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import (
    init_db,
    get_all_trades
)

import requests
import os
import pandas as pd

from app.scanner import scan_markets
from app.trade_manager import manage_trades
from app.analytics import get_analytics
from app.diagnostics import get_diagnostics

app = FastAPI()

# --------------------------------
# ENSURE CSV EXISTS
# --------------------------------

def ensure_signals_file():

    if not os.path.exists(
        "signals.csv"
    ):

        columns = [

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

            "entry_price",

            "sl",

            "tp",

            "rr",

            "trade_status"
        ]

        df = pd.DataFrame(
            columns=columns
        )

        df.to_csv(
            "signals.csv",
            index=False
        )

        print(
            "signals.csv CREATED"
        )

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# SCHEDULER
# -----------------------------------

scheduler = BackgroundScheduler()

# -----------------------------------
# AUTOMATED SCAN LOOP
# -----------------------------------

def scheduled_scan():

    print(
        "RUNNING AUTOMATED SCAN..."
    )

    manage_trades()

    signals = scan_markets()

    print(
        "SCAN COMPLETE"
    )

    for signal in signals:

        if "pair" in signal:

            print(
                signal["pair"],
                signal["signal"],
                signal["setup_score"]
            )

# -----------------------------------
# STARTUP
# -----------------------------------

@app.on_event("startup")
def startup_event():

    ensure_signals_file()

    init_db()

    print(
        "STARTING SCHEDULER..."
    )

    scheduler.add_job(
        scheduled_scan,
        "interval",
        minutes=5
    )

    scheduler.start()

    print(
        "SCHEDULER STARTED"
    )

# -----------------------------------
# SHUTDOWN
# -----------------------------------

@app.on_event("shutdown")
def shutdown_event():

    scheduler.shutdown()

# -----------------------------------
# ROOT
# -----------------------------------

@app.get("/")
def root():

    return {

        "message":
            "Forex AI Radar Backend Running"
    }

# -----------------------------------
# SIGNALS
# -----------------------------------

@app.get("/signals")
def get_signals():

    return scan_markets()

# -----------------------------------
# FORCE SCAN
# -----------------------------------

@app.get("/force-scan")
def force_scan():

    print(
        "MANUAL FORCE SCAN"
    )

    manage_trades()

    signals = scan_markets()

    return {

        "message":
            "Manual scan complete",

        "signals":
            signals
    }

# -----------------------------------
# ANALYTICS
# -----------------------------------

@app.get("/analytics")
def analytics():

    return get_analytics()

# -----------------------------------
# DIAGNOSTICS
# -----------------------------------

@app.get("/diagnostics")
def diagnostics():

    return get_diagnostics()

# -----------------------------------
# TELEGRAM TEST
# -----------------------------------

@app.get("/test-telegram")
def test_telegram():

    token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    message = (
        "🚀 Railway Telegram "
        "Test Success"
    )

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    response = requests.post(
        url,
        json={

            "chat_id":
                chat_id,

            "text":
                message
        }
    )

    return {

        "status_code":
            response.status_code,

        "response":
            response.text
    }

# -----------------------------------
# TEST TRADE
# -----------------------------------

@app.get("/test-trade")
def test_trade():

    import pandas as pd

    test_row = {

        "signal_id":
            "test123",

        "timestamp":
            "2026-05-09T00:00:00+00:00",

        "pair":
            "EURUSD=X",

        "signal":
            "BUY",

        "bias":
            "BULLISH",

        "setup_quality":
            "HIGH",

        "setup_score":
            90,

        "market_session":
            "NEW_YORK",

        "rsi":
            55,

        "atr_percent":
            0.0005,

        "candle_strength":
            0.6,

        "execution_ready":
            True,

        "execution_reason":
            "Test trade",

        "entry_price":
            1.1000,

        "sl":
            1.0000,

        "tp":
            1.0500,

        "rr":
            2.0,

        "trade_status":
            "OPEN"
    }

    try:

        df = pd.read_csv(
            "signals.csv"
        )

    except:

        df = pd.DataFrame()

    df = pd.concat([
        df,
        pd.DataFrame([test_row])
    ])

    df.to_csv(
        "signals.csv",
        index=False
    )

    return {

        "message":
            "Test trade added"
    }

# -----------------------------------
# RUN TRADE MANAGER
# -----------------------------------

@app.get("/run-trade-manager")
def run_trade_manager():

    manage_trades()

    return {

        "message":
            "Trade manager executed"
    }

# -----------------------------------
# VIEW TRADES
# -----------------------------------

@app.get("/view-trades")
def view_trades():

    return get_all_trades()