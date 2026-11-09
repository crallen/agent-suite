"""SQLite storage for orders. The schema lives in migrations/, applied in order."""

import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    migrate(conn)
    return conn


def migrate(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
    applied = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
    for script in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if script.name in applied:
            continue
        conn.executescript(script.read_text())
        conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (script.name,))
        conn.commit()


class OrderRepo:
    def __init__(self, conn):
        self._conn = conn

    def create(self, customer_email, amount_cents):
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO orders (customer_email, amount_cents) VALUES (?, ?)",
                (customer_email, amount_cents),
            )
        return cursor.lastrowid

    def get(self, order_id):
        row = self._conn.execute(
            "SELECT id, customer_email, amount_cents, status FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        return dict(row) if row else None

    def set_status(self, order_id, status):
        with self._conn:
            self._conn.execute(
                "UPDATE orders SET status = ? WHERE id = ?", (status, order_id)
            )
