import ccxt
import psycopg2
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
EXCHANGE  = ccxt.binance()
SYMBOL    = 'BTC/USDT'
TIMEFRAME = '1m'
DB = {
    'dbname':   'spectra',
    'user':     'spectra_user',
    'password': 'very_secret_pass',
    'host':     'timescaledb',
    'port':     5432
}
# ────────────────────────────────────────────────────────────────────────────────

def wait_for_db():
    """Wait until TimescaleDB is accepting connections."""
    while True:
        try:
            conn = psycopg2.connect(**DB)
            print(f"[{datetime.utcnow()}] Connected to database")
            return conn
        except psycopg2.OperationalError:
            print(f"[{datetime.utcnow()}] Database not ready, retrying in 5s…")
            time.sleep(5)

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS btc_usdt_ohlcv (
                timestamp TIMESTAMPTZ PRIMARY KEY,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION
            );
        """)
        conn.commit()

def insert_data(conn, candles):
    with conn.cursor() as cur:
        for c in candles:
            ts = datetime.utcfromtimestamp(c[0] / 1000)
            cur.execute("""
                INSERT INTO btc_usdt_ohlcv
                  (timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING;
            """, (ts, c[1], c[2], c[3], c[4], c[5]))
        conn.commit()

if __name__ == "__main__":
    conn = wait_for_db()
    create_table(conn)
    while True:
        try:
            candles = EXCHANGE.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=50)
            insert_data(conn, candles)
            print(f"[{datetime.utcnow()}] Inserted {len(candles)} candles.")
        except Exception as e:
            print(f"[{datetime.utcnow()}] Error:", e)
        time.sleep(60)
