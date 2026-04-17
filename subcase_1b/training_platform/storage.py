import os
import sqlite3
import time
import json
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
            output_file TEXT,
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT,
            username TEXT,
            score REAL,
            flag TEXT,
            duration REAL,
            details TEXT,
            created_at REAL NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS quiz_results (
            course_id TEXT NOT NULL,
            username TEXT NOT NULL,
            answers TEXT NOT NULL,
            score REAL NOT NULL DEFAULT 0,
            updated_at REAL NOT NULL,
            PRIMARY KEY(course_id, username)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS edx_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT,
            username TEXT,
            error TEXT NOT NULL,
            timestamp REAL NOT NULL
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

        # Backward-compatible migrations for existing databases.
        results_columns = {
            row['name']
            for row in conn.execute("PRAGMA table_info(results)").fetchall()
        }
        if 'flag' not in results_columns:
            conn.execute('ALTER TABLE results ADD COLUMN flag TEXT')
        if 'duration' not in results_columns:
            conn.execute('ALTER TABLE results ADD COLUMN duration REAL')

        jobs_columns = {
            row['name']
            for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
        }
        if 'output_file' not in jobs_columns:
            conn.execute('ALTER TABLE jobs ADD COLUMN output_file TEXT')


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


def upsert_progress(course_id, username, value):
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO progress(course_id, username, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(course_id, username)
            DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            ''',
            (course_id, username, value, time.time()),
        )


def get_progress(course_id, username, default=0):
    with _connect() as conn:
        row = conn.execute(
            'SELECT value FROM progress WHERE course_id = ? AND username = ?',
            (course_id, username),
        ).fetchone()
    return row['value'] if row else default


def upsert_quiz_result(course_id, username, answers, score):
    payload = json.dumps(answers or {})
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO quiz_results(course_id, username, answers, score, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(course_id, username)
            DO UPDATE SET
                answers = excluded.answers,
                score = excluded.score,
                updated_at = excluded.updated_at
            ''',
            (course_id, username, payload, score, time.time()),
        )


def get_quiz_result(course_id, username):
    with _connect() as conn:
        row = conn.execute(
            '''
            SELECT answers, score
            FROM quiz_results
            WHERE course_id = ? AND username = ?
            ''',
            (course_id, username),
        ).fetchone()
    if not row:
        return None
    try:
        answers = json.loads(row['answers']) if row['answers'] else {}
    except json.JSONDecodeError:
        answers = {}
    return {'answers': answers, 'score': row['score']}


def append_edx_failure(course_id, username, error, timestamp=None):
    value = timestamp if timestamp is not None else time.time()
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO edx_failures(course_id, username, error, timestamp)
            VALUES (?, ?, ?, ?)
            ''',
            (course_id, username, error, value),
        )


def list_edx_failures():
    with _connect() as conn:
        rows = conn.execute(
            '''
            SELECT course_id, username, error, timestamp
            FROM edx_failures
            ORDER BY id ASC
            '''
        ).fetchall()
    return [dict(row) for row in rows]


def create_job(job_id, tool, status='pending'):
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO jobs(id, status, tool, output, output_file, created_at)
            VALUES (?, ?, ?, NULL, NULL, ?)
            ''',
            (job_id, status, tool, time.time()),
        )


def update_job(job_id, **fields):
    if not fields:
        return
    allowed = {'status', 'tool', 'output', 'output_file'}
    updates = [(key, value) for key, value in fields.items() if key in allowed]
    if not updates:
        return
    clause = ', '.join(f'{key} = ?' for key, _ in updates)
    values = [value for _, value in updates] + [job_id]
    with _connect() as conn:
        conn.execute(f'UPDATE jobs SET {clause} WHERE id = ?', values)


def get_job(job_id):
    with _connect() as conn:
        row = conn.execute(
            '''
            SELECT id, status, tool, output, output_file
            FROM jobs
            WHERE id = ?
            ''',
            (job_id,),
        ).fetchone()
    if not row:
        return None
    job = dict(row)
    job.pop('id', None)
    return job


def append_result_record(result):
    with _connect() as conn:
        conn.execute(
            '''
            INSERT INTO results(course_id, username, score, flag, duration, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                result.get('course_id'),
                result.get('username'),
                result.get('score', 0),
                result.get('flag'),
                result.get('duration'),
                json.dumps(result.get('details', {})),
                result.get('timestamp', time.time()),
            ),
        )


def aggregate_result_metrics(course_id, username):
    with _connect() as conn:
        total_row = conn.execute(
            '''
            SELECT COALESCE(SUM(score), 0) AS total_score
            FROM results
            WHERE course_id = ? AND username = ?
            ''',
            (course_id, username),
        ).fetchone()
        flags_rows = conn.execute(
            '''
            SELECT DISTINCT flag
            FROM results
            WHERE course_id = ? AND username = ? AND flag IS NOT NULL AND flag != ''
            ORDER BY flag ASC
            ''',
            (course_id, username),
        ).fetchall()
    return {
        'score': total_row['total_score'] if total_row else 0,
        'flags': [row['flag'] for row in flags_rows],
    }
