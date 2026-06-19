import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis import insights
from config import DB_PATH

st.set_page_config(
    page_title="IT Incident Intelligence",
    page_icon=":bar_chart:",
    layout="wide",
)


@st.cache_data(ttl=300)
def load_df(query_name: str) -> pd.DataFrame:
    return getattr(insights, query_name)()


@st.cache_data(ttl=300)
def load_summary() -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        totals = pd.read_sql(
            """
            SELECT
                COUNT(*) AS total_tickets,
                SUM(sla_breached) AS sla_breaches,
                ROUND(AVG(resolution_hours), 2) AS avg_resolution_hr,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) AS open_tickets
            FROM tickets
            """,
            conn,
        ).iloc[0]
        assets_count = pd.read_sql("SELECT COUNT(*) c FROM assets", conn).iloc[0]["c"]
        non_compliant = pd.read_sql(
            "SELECT COUNT(*) c FROM assets WHERE compliance_status = 'Non-compliant'",
            conn,
        ).iloc[0]["c"]
    return {
        "total_tickets": int(totals["total_tickets"] or 0),
        "sla_breaches": int(totals["sla_breaches"] or 0),
        "avg_resolution_hr": float(totals["avg_resolution_hr"] or 0),
        "open_tickets": int(totals["open_tickets"] or 0),
        "asset_count": int(assets_count),
        "non_compliant_assets": int(non_compliant),
    }


def kpis():
    if not DB_PATH.exists():
        st.error(
            f"Database not found at {DB_PATH}. "
            "Run `python -m etl.run_pipeline` first."
        )
        st.stop()
    s = load_summary()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total tickets", f"{s['total_tickets']:,}")
    c2.metric("Open tickets", f"{s['open_tickets']:,}")
    c3.metric("SLA breaches", f"{s['sla_breaches']:,}")
    c4.metric("Avg resolution (hr)", f"{s['avg_resolution_hr']:.1f}")
    c5.metric("Assets tracked", f"{s['asset_count']:,}")
    c6.metric("Non-compliant", f"{s['non_compliant_assets']:,}")


def section_volume():
    st.subheader("Ticket volume over time")
    df = load_df("daily_volume")
    if df.empty:
        st.info("No data")
        return
    df["day"] = pd.to_datetime(df["day"])
    fig = px.line(
        df,
        x="day",
        y=["ticket_count", "sla_breaches"],
        labels={"value": "Tickets", "day": "Date", "variable": "Series"},
    )
    st.plotly_chart(fig, use_container_width=True)


def section_categories():
    left, right = st.columns(2)
    with left:
        st.subheader("Tickets by category")
        df = load_df("category_volume")
        if not df.empty:
            fig = px.bar(df, x="category_name", y="ticket_count", color="category_name")
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Tickets")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Priority breakdown")
        df = load_df("priority_breakdown")
        if not df.empty:
            fig = px.pie(df, names="priority", values="ticket_count", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)


def section_devices():
    st.subheader("Devices generating the most tickets")
    df = load_df("top_devices")
    if df.empty:
        st.info("No data")
        return
    fig = px.bar(
        df.head(10),
        x="model",
        y="ticket_count",
        color="asset_type",
        hover_data=["avg_resolution_hr", "sla_breaches"],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Tickets")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def section_departments():
    st.subheader("Departments by ticket volume")
    df = load_df("top_departments")
    if df.empty:
        st.info("No data")
        return
    fig = px.bar(
        df,
        x="dept_name",
        y="ticket_count",
        color="location",
        hover_data=["avg_resolution_hr", "sla_breaches"],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Tickets")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def section_repeats():
    st.subheader("Repeating weekly issues")
    df = load_df("repeat_keywords")
    if df.empty:
        st.info("No data")
        return
    fig = px.scatter(
        df,
        x="weeks_seen",
        y="total_hits",
        size="avg_per_week",
        color="keyword",
        hover_name="keyword",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def section_kb():
    st.subheader("Knowledge base coverage gaps")
    df = load_df("kb_gaps")
    if df.empty:
        st.info("No data")
        return
    df_view = df.copy()
    df_view["status_color"] = df_view["kb_coverage"]
    fig = px.bar(
        df_view.head(20),
        x="keyword",
        y="hits",
        color="kb_coverage",
        color_discrete_map={"Covered": "#2E8B57", "No KB": "#C0392B"},
    )
    fig.update_layout(xaxis_title="", yaxis_title="Tickets matched")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def section_assets():
    st.subheader("Assets near end-of-life or non-compliant")
    df = load_df("assets_near_eol")
    if df.empty:
        st.info("No data")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def section_reporters():
    st.subheader("Top reporters (potential targeted training)")
    df = load_df("repeat_offenders")
    if df.empty:
        st.info("No data")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    st.title("IT Incident Intelligence")
    st.caption("Reducing repeat incidents by blending tickets, assets, and KB content.")
    kpis()
    st.divider()
    tabs = st.tabs(
        [
            "Overview",
            "Devices",
            "Departments",
            "Repeating issues",
            "KB gaps",
            "Assets",
            "Reporters",
        ]
    )
    with tabs[0]:
        section_volume()
        section_categories()
    with tabs[1]:
        section_devices()
    with tabs[2]:
        section_departments()
    with tabs[3]:
        section_repeats()
    with tabs[4]:
        section_kb()
    with tabs[5]:
        section_assets()
    with tabs[6]:
        section_reporters()


if __name__ == "__main__":
    main()
