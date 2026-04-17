import os
import sqlite3
import time
from contextlib import contextmanager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_DB_PATH = os.getenv(
    'TRAINING_DB_PATH',
    os.path.join(BASE_DIR, 'training_platform.sqlite3'),
)


@contextmanager
def _connect():
    conn = sqlite3.connect(TRAINING_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_schema():
    """Create required tables if they do not exist."""

    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'trainee',
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created_at REAL NOT NULL,
            issued_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            revoked_at REAL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            instructor TEXT,
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS invites (
            code TEXT PRIMARY KEY,
            course_id TEXT,
            email TEXT,
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS progress (
            course_id TEXT NOT NULL,
            username TEXT NOT NULL,
            value REAL NOT NULL DEFAULT 0,
            updated_at REAL NOT NULL,
            PRIMARY KEY(course_id, username)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            tool TEXT NOT NULL,
            output TEXT,
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT,
            username TEXT,
            score REAL,
            details TEXT,
            created_at REAL NOT NULL
        )
        """,
    ]
    with _connect() as conn:
        for stmt in statements:
            conn.execute(stmt)

        # Backward-compatible migrations for existing databases created before
        # session metadata was introduced.
        session_columns = {
            row['name']
            for row in conn.execute("PRAGMA table_info(sessions)").fetchall()
        }
        if 'issued_at' not in session_columns:
            conn.execute('ALTER TABLE sessions ADD COLUMN issued_at REAL')
        if 'expires_at' not in session_columns:
            conn.execute('ALTER TABLE sessions ADD COLUMN expires_at REAL')
        if 'revoked_at' not in session_columns:
            conn.execute('ALTER TABLE sessions ADD COLUMN revoked_at REAL')

        now = time.time()
        conn.execute(
            '''
            UPDATE sessions
            SET issued_at = COALESCE(issued_at, created_at),
                expires_at = COALESCE(expires_at, created_at + 3600)
            WHERE issued_at IS NULL OR expires_at IS NULL
            ''',
        )


def get_user(username):
    with _connect() as conn:
        row = conn.execute(
            'SELECT username, password, role FROM users WHERE username = ?',
            (username,),
        ).fetchone()
    return dict(row) if row else None


def create_user(username, password, role='trainee'):
    with _connect() as conn:
        conn.execute(
            'INSERT INTO users(username, password, role, created_at) VALUES (?, ?, ?, ?)',
            (username, password, role, time.time()),
        )


def create_session(token, username, issued_at, expires_at):
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO sessions(token, username, created_at, issued_at, expires_at, revoked_at)
            VALUES (?, ?, ?, ?, ?, NULL)
            ''',
            (token, username, issued_at, issued_at, expires_at),
        )


def get_session_by_token(token):
    with _connect() as conn:
        row = conn.execute(
            '''
            SELECT token, username, issued_at, expires_at, revoked_at
            FROM sessions
            WHERE token = ?
            ''',
            (token,),
        ).fetchone()
    return dict(row) if row else None


def revoke_session(token, revoked_at=None):
    revoked_at = revoked_at if revoked_at is not None else time.time()
    with _connect() as conn:
        result = conn.execute(
            'UPDATE sessions SET revoked_at = ? WHERE token = ? AND revoked_at IS NULL',
            (revoked_at, token),
        )
    return result.rowcount > 0
