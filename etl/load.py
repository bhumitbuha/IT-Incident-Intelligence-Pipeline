import sqlite3

import pandas as pd

from config import DB_DIR, DB_PATH, SCHEMA_PATH
from etl.logger import get_logger
from etl.transform import CleanData

log = get_logger("load")


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    log.info("Applying schema %s", SCHEMA_PATH.name)
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def _insert(conn, table: str, df: pd.DataFrame) -> None:
    if df.empty:
        log.warning("Skip %s (empty)", table)
        return
    df.to_sql(table, conn, if_exists="append", index=False)
    log.info("Loaded %d rows into %s", len(df), table)


def load(clean: CleanData) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = _connect()
    try:
        apply_schema(conn)
        _insert(conn, "departments", clean.departments)
        _insert(conn, "users", clean.users)
        _insert(conn, "assets", clean.assets)
        _insert(conn, "ticket_categories", clean.categories)
        _insert(conn, "tickets", clean.tickets)
        _insert(conn, "ticket_keywords", clean.ticket_keywords)
        _insert(conn, "kb_articles", clean.kb_articles)
        _insert(conn, "kb_keywords", clean.kb_keywords)
        _insert(conn, "resolution_metrics", clean.resolution_metrics)
        conn.commit()
    finally:
        conn.close()
    log.info("Database written to %s", DB_PATH)
