import sqlite3

DB_FILE = "trades.db"

# --------------------------------
# CONNECT DATABASE
# --------------------------------

def get_connection():

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.row_factory = sqlite3.Row

    return conn

# --------------------------------
# CREATE TABLE
# --------------------------------

def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS trades (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            signal_id TEXT,

            timestamp TEXT,

            pair TEXT,

            signal TEXT,

            bias TEXT,

            setup_quality TEXT,

            setup_score REAL,

            market_session TEXT,

            rsi REAL,

            atr_percent REAL,

            candle_strength REAL,

            execution_ready INTEGER,

            execution_reason TEXT,

            entry_price REAL,

            sl REAL,

            tp REAL,

            rr REAL,

            trade_status TEXT
        )
        '''
    )

    conn.commit()

    conn.close()

    print("DATABASE READY")



    # --------------------------------
# INSERT TRADE
# --------------------------------

def insert_trade(trade):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO trades (

            signal_id,
            timestamp,
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
            entry_price,
            sl,
            tp,
            rr,
            trade_status

        )

        VALUES (

            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?

        )
        ''',

        (

            trade["signal_id"],
            trade["timestamp"],
            trade["pair"],
            trade["signal"],
            trade["bias"],
            trade["setup_quality"],
            trade["setup_score"],
            trade["market_session"],
            trade["rsi"],
            trade["atr_percent"],
            trade["candle_strength"],
            int(trade["execution_ready"]),
            trade["execution_reason"],
            trade["entry_price"],
            trade["sl"],
            trade["tp"],
            trade["rr"],
            trade["trade_status"]

        )
    )

    conn.commit()

    conn.close()