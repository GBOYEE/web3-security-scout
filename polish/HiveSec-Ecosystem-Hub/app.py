#!/usr/bin/env python3
"""
HiveSec Ecosystem Hub — Dashboard for XANDER Operator.
Shows recent tasks and status. Simple, secure.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="HiveSec Hub", layout="wide")

# Config
DB_PATH = os.getenv("TASKS_DB", "/root/.openclaw/workspace/memory/tasks.db")

st.title("🛰 HiveSec Ecosystem Hub")
st.markdown("Live view of XANDER Operator task queue.")

@st.cache_data(ttl=5)
def load_tasks(limit=200):
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT
                substr(id,1,8) as short_id,
                description,
                type,
                status,
                datetime(created) as created,
                attempts,
                last_error
            FROM tasks
            ORDER BY datetime(created) DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"DB error: {e}")
        return pd.DataFrame()

df = load_tasks()
if df.empty:
    st.warning("No tasks found or database unavailable.")
else:
    st.dataframe(df, use_container_width=True)
    st.caption(f"Showing {len(df)} recent tasks")

# Simple stats
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total tasks", len(df))
    col2.metric("Pending", (df['status']=='pending').sum())
    col3.metric("Failed", (df['status']=='failed').sum())
