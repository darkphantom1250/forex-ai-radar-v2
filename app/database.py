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