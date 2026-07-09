"""
Database layer — SQLite by default.
To switch to MySQL: replace sqlite3 calls with `mysql-connector-python`
and update CREATE TABLE syntax (AUTO_INCREMENT instead of AUTOINCREMENT).
Schema stays identical, so the rest of the app doesn't need to change.
"""
import sqlite3
from datetime import datetime

DB_PATH = "leads.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            name TEXT,
            need TEXT,
            budget TEXT,
            timeline TEXT,
            score TEXT DEFAULT 'Unqualified',
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            sender TEXT,
            message TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_message(chat_id, sender, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (chat_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
        (chat_id, sender, message, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def upsert_lead(chat_id, name=None, need=None, budget=None, timeline=None, score=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM leads WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    if row:
        c.execute(
            """UPDATE leads SET
               name = COALESCE(?, name),
               need = COALESCE(?, need),
               budget = COALESCE(?, budget),
               timeline = COALESCE(?, timeline),
               score = COALESCE(?, score)
               WHERE chat_id = ?""",
            (name, need, budget, timeline, score, chat_id),
        )
    else:
        c.execute(
            """INSERT INTO leads (chat_id, name, need, budget, timeline, score, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chat_id, name, need, budget, timeline, score or "Unqualified", datetime.utcnow().isoformat()),
        )
    conn.commit()
    conn.close()


def get_all_leads():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_messages(chat_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
