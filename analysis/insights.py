import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import queries
from config import DB_PATH


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run etl.run_pipeline first."
        )
    return sqlite3.connect(DB_PATH)


def run_query(sql: str) -> pd.DataFrame:
    with _connect() as conn:
        return pd.read_sql(sql, conn)


def top_devices() -> pd.DataFrame:
    return run_query(queries.TOP_DEVICES)


def top_departments() -> pd.DataFrame:
    return run_query(queries.TOP_DEPARTMENTS)


def repeat_keywords() -> pd.DataFrame:
    return run_query(queries.REPEAT_KEYWORDS_WEEKLY)


def category_volume() -> pd.DataFrame:
    return run_query(queries.CATEGORY_VOLUME)


def kb_gaps() -> pd.DataFrame:
    return run_query(queries.KB_GAPS)


def assets_near_eol() -> pd.DataFrame:
    return run_query(queries.ASSETS_NEAR_EOL)


def daily_volume() -> pd.DataFrame:
    return run_query(queries.DAILY_VOLUME)


def priority_breakdown() -> pd.DataFrame:
    return run_query(queries.PRIORITY_BREAKDOWN)


def repeat_offenders() -> pd.DataFrame:
    return run_query(queries.REPEAT_OFFENDERS)


REPORTS = [
    ("Top problem devices", top_devices),
    ("Top departments by ticket volume", top_departments),
    ("Repeat weekly issues", repeat_keywords),
    ("Category breakdown", category_volume),
    ("Knowledge base coverage gaps", kb_gaps),
    ("Assets near end-of-life", assets_near_eol),
    ("Priority breakdown", priority_breakdown),
    ("Top reporters", repeat_offenders),
]


def print_all_reports() -> None:
    pd.set_option("display.max_rows", 25)
    pd.set_option("display.width", 160)
    for title, fn in REPORTS:
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)
        df = fn()
        if df.empty:
            print("(no rows)")
        else:
            print(df.to_string(index=False))


if __name__ == "__main__":
    print_all_reports()
