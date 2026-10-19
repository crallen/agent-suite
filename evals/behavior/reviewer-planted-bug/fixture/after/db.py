"""User lookups against the app's SQLite database."""

import sqlite3


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_user(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_user_by_email(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT id, name, email FROM users WHERE email = ?", (email,)
    ).fetchone()


def search_users(conn: sqlite3.Connection, search_box_text: str) -> list[sqlite3.Row]:
    return conn.execute(f"SELECT id, name, email FROM users WHERE name LIKE '%{search_box_text}%'").fetchall()
