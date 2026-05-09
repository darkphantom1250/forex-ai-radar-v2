from apscheduler.schedulers.background import BackgroundScheduler

from app.scanner import scan_markets
from app.trade_manager import update_trade_status

scheduler = BackgroundScheduler()

# --------------------------------
# MAIN SCAN LOOP
# --------------------------------

def scheduled_scan():

    print("RUNNING AUTOMATED SCAN...")

    # update old trades
    update_trade_status()

    # scan markets
    signals = scan_markets()

    print("SCAN COMPLETE")

    # optional logging
    for signal in signals:

        print(
            signal["pair"],
            signal["signal"],
            signal["setup_score"]
        )

# --------------------------------
# START SCHEDULER
# --------------------------------

scheduler.add_job(
    scheduled_scan,
    "interval",
    minutes=5
)

scheduler.start()

print("SCHEDULER STARTED")