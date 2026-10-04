import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forex.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        entry REAL NOT NULL,
        stop REAL NOT NULL,
        target REAL NOT NULL,
        status TEXT DEFAULT 'open'
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        signal TEXT NOT NULL,
        confidence INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def seed_positions():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM positions").fetchone()[0]
    if count == 0:
        conn.execute(
            "INSERT INTO positions (symbol, side, entry, stop, target, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("XAUUSD", "BUY", 3821.5, 3808.0, 3865.0, "open"),
        )
        conn.execute(
            "INSERT INTO positions (symbol, side, entry, stop, target, status) VALUES (?, ?, ?, ?, ?, ?)",
            ("EURUSD", "SELL", 1.1712, 1.1756, 1.1668, "open"),
        )
        conn.commit()
    conn.close()
