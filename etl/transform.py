from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd

from config import SLA_HOURS
from etl.extract import RawData
from etl.keywords import extract_keywords, map_to_category
from etl.logger import get_logger

log = get_logger("transform")


@dataclass
class CleanData:
    departments: pd.DataFrame
    users: pd.DataFrame
    assets: pd.DataFrame
    tickets: pd.DataFrame
    ticket_keywords: pd.DataFrame
    categories: pd.DataFrame
    kb_articles: pd.DataFrame
    kb_keywords: pd.DataFrame
    resolution_metrics: pd.DataFrame


def _clean_departments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["dept_id"].str.strip() != ""]
    df["dept_name"] = df["dept_name"].str.strip()
    df["location"] = df["location"].str.strip()
    return df.drop_duplicates(subset=["dept_id"])


def _clean_users(df: pd.DataFrame, dept_ids: set) -> pd.DataFrame:
    before = len(df)
    df = df.copy()
    df["full_name"] = df["full_name"].str.strip()
    df["email"] = df["email"].str.strip().str.lower()
    df["dept_id"] = df["dept_id"].str.strip()
    df = df[df["full_name"] != ""]
    df = df[df["email"] != ""]
    df = df[df["dept_id"].isin(dept_ids)]
    df = df.drop_duplicates(subset=["email"], keep="first")
    df = df.drop_duplicates(subset=["user_id"], keep="first")
    log.info("Users: %d -> %d after cleaning", before, len(df))
    return df


def _clean_assets(df: pd.DataFrame, user_ids: set) -> pd.DataFrame:
    before = len(df)
    df = df.copy()
    df = df.drop_duplicates(subset=["asset_id"], keep="first")
    df = df.drop_duplicates(subset=["asset_tag"], keep="first")
    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
    df["warranty_end"] = pd.to_datetime(df["warranty_end"], errors="coerce")
    today = pd.Timestamp(datetime.utcnow().date())
    df["age_years"] = ((today - df["purchase_date"]).dt.days / 365.25).round(2)
    df.loc[~df["assigned_user_id"].isin(user_ids), "assigned_user_id"] = None
    df["purchase_date"] = df["purchase_date"].dt.strftime("%Y-%m-%d")
    df["warranty_end"] = df["warranty_end"].dt.strftime("%Y-%m-%d")
    log.info("Assets: %d -> %d after cleaning", before, len(df))
    return df


def _clean_tickets(df: pd.DataFrame, user_ids: set, asset_tags: set) -> pd.DataFrame:
    before = len(df)
    df = df.copy()
    df = df.drop_duplicates(subset=["ticket_id"], keep="first")
    df["short_description"] = df["short_description"].fillna("").str.strip()
    df["resolution_notes"] = df["resolution_notes"].fillna("").str.strip()
    df["raw_category"] = df["raw_category"].fillna("").str.strip()
    df["priority"] = df["priority"].where(df["priority"].isin(SLA_HOURS), "Medium")

    df["opened_at"] = pd.to_datetime(df["opened_at"], errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")

    df = df[df["opened_at"].notna()]
    df = df[df["short_description"] != ""]

    df.loc[~df["reporter_user_id"].isin(user_ids), "reporter_user_id"] = None
    df.loc[~df["asset_tag"].isin(asset_tags), "asset_tag"] = None

    df["resolution_hours"] = pd.to_numeric(df["resolution_hours"], errors="coerce")
    mask_closed = df["status"].isin(["Closed", "Resolved"]) & df["closed_at"].notna()
    derived = (df["closed_at"] - df["opened_at"]).dt.total_seconds() / 3600.0
    df.loc[mask_closed & df["resolution_hours"].isna(), "resolution_hours"] = derived

    sla = df["priority"].map(SLA_HOURS)
    df["sla_breached"] = ((df["resolution_hours"] > sla) & mask_closed).astype(int)

    df["opened_at"] = df["opened_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["closed_at"] = df["closed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

    log.info("Tickets: %d -> %d after cleaning", before, len(df))
    return df


def _build_keywords_and_categories(tickets: pd.DataFrame):
    rows = []
    categories = []
    for _, t in tickets.iterrows():
        text = f"{t['short_description']} {t['resolution_notes']}"
        kws = extract_keywords(text)
        cat = map_to_category(kws, t["raw_category"])
        categories.append(cat)
        for kw in kws:
            rows.append({"ticket_id": t["ticket_id"], "keyword": kw})
    tickets = tickets.copy()
    tickets["category_name"] = categories
    keywords_df = pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame(
        columns=["ticket_id", "keyword"]
    )
    return tickets, keywords_df


def _build_category_table(tickets: pd.DataFrame) -> pd.DataFrame:
    cats = sorted(tickets["category_name"].dropna().unique().tolist())
    return pd.DataFrame(
        {"category_id": range(1, len(cats) + 1), "category_name": cats}
    )


def _attach_category_id(tickets: pd.DataFrame, categories: pd.DataFrame) -> pd.DataFrame:
    lookup = dict(zip(categories["category_name"], categories["category_id"]))
    out = tickets.copy()
    out["category_id"] = out["category_name"].map(lookup)
    return out


def _build_metrics(tickets: pd.DataFrame) -> pd.DataFrame:
    df = tickets.copy()
    df = df[df["resolution_hours"].notna()]
    if df.empty:
        return pd.DataFrame(
            columns=[
                "metric_date",
                "category_name",
                "priority",
                "ticket_count",
                "avg_resolution_hr",
                "breaches",
            ]
        )
    df["metric_date"] = pd.to_datetime(df["opened_at"]).dt.strftime("%Y-%m-%d")
    grouped = (
        df.groupby(["metric_date", "category_name", "priority"], as_index=False)
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_resolution_hr=("resolution_hours", "mean"),
            breaches=("sla_breached", "sum"),
        )
    )
    grouped["avg_resolution_hr"] = grouped["avg_resolution_hr"].round(2)
    return grouped


def _kb_to_df(kb_articles: list):
    article_rows = []
    keyword_rows = []
    for art in kb_articles:
        kws = art.get("keywords", [])
        article_rows.append(
            {
                "kb_id": art["kb_id"],
                "title": art["title"],
                "category": art.get("category", ""),
                "keywords": ",".join(kws),
                "body": art.get("body", ""),
            }
        )
        for kw in kws:
            keyword_rows.append({"kb_id": art["kb_id"], "keyword": kw.lower().strip()})
    articles_df = pd.DataFrame(article_rows)
    keywords_df = (
        pd.DataFrame(keyword_rows).drop_duplicates()
        if keyword_rows
        else pd.DataFrame(columns=["kb_id", "keyword"])
    )
    return articles_df, keywords_df


def transform(raw: RawData) -> CleanData:
    departments = _clean_departments(raw.departments)
    dept_ids = set(departments["dept_id"])
    users = _clean_users(raw.users, dept_ids)
    user_ids = set(users["user_id"])
    assets = _clean_assets(raw.assets, user_ids)
    asset_tags = set(assets["asset_tag"])
    tickets = _clean_tickets(raw.tickets, user_ids, asset_tags)
    tickets, keywords_df = _build_keywords_and_categories(tickets)
    categories = _build_category_table(tickets)
    tickets = _attach_category_id(tickets, categories)
    metrics = _build_metrics(tickets)
    kb, kb_kw = _kb_to_df(raw.kb_articles)

    tickets_out = tickets[
        [
            "ticket_id",
            "opened_at",
            "closed_at",
            "status",
            "priority",
            "category_id",
            "short_description",
            "resolution_notes",
            "reporter_user_id",
            "asset_tag",
            "resolution_hours",
            "sla_breached",
        ]
    ].copy()
    tickets_out["resolution_hours"] = tickets_out["resolution_hours"].replace(
        {np.nan: None}
    )
    tickets_out = tickets_out.where(pd.notna(tickets_out), None)

    log.info(
        "Transform complete: %d tickets, %d keywords, %d categories",
        len(tickets_out),
        len(keywords_df),
        len(categories),
    )
    return CleanData(
        departments=departments,
        users=users,
        assets=assets,
        tickets=tickets_out,
        ticket_keywords=keywords_df,
        categories=categories,
        kb_articles=kb,
        kb_keywords=kb_kw,
        resolution_metrics=metrics,
    )
