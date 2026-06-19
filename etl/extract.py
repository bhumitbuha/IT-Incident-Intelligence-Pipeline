import json
from dataclasses import dataclass

import pandas as pd

from config import (
    RAW_ASSETS,
    RAW_DEPARTMENTS,
    RAW_KB,
    RAW_TICKETS,
    RAW_USERS,
)
from etl.logger import get_logger

log = get_logger("extract")


@dataclass
class RawData:
    tickets: pd.DataFrame
    users: pd.DataFrame
    assets: pd.DataFrame
    departments: pd.DataFrame
    kb_articles: list


def read_csv(path):
    log.info("Reading %s", path.name)
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    log.info("  -> %d rows", len(df))
    return df


def read_kb(path):
    log.info("Reading %s", path.name)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    log.info("  -> %d articles", len(data))
    return data


def extract() -> RawData:
    return RawData(
        tickets=read_csv(RAW_TICKETS),
        users=read_csv(RAW_USERS),
        assets=read_csv(RAW_ASSETS),
        departments=read_csv(RAW_DEPARTMENTS),
        kb_articles=read_kb(RAW_KB),
    )
