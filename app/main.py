from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# start scheduler
import app.scheduler

from app.scanner import scan_markets
from app.trade_manager import update_trade_status
from app.analytics import get_analytics
from app.diagnostics import get_diagnostics

app = FastAPI()

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
# ROOT
# -----------------------------------

@app.get("/")
def root():

    return {
        "message": "Forex AI Radar Backend Running"
    }

# -----------------------------------
# SIGNALS
# -----------------------------------

@app.get("/signals")
def get_signals():

    signals = scan_markets()

    return signals

# -----------------------------------
# FORCE SCAN
# -----------------------------------

@app.get("/force-scan")
def force_scan():

    print("MANUAL FORCE SCAN")

    # update active trades
    update_trade_status()

    # scan markets
    signals = scan_markets()

    return {
        "message": "Manual scan complete",
        "signals": signals
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