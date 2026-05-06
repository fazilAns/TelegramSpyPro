import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Spy Pro Dashboard", layout="wide")
st.title("🛡️ Telegram Spy Pro - Analytics")

def get_data():
    conn = sqlite3.connect('spy_pro_data.db')
    df = pd.read_sql_query("SELECT * FROM activity", conn)
    conn.close()
    return df

try:
    df = get_data()
    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("Total Messages Logged", len(df))
        col2.metric("Unique Users Tracked", df['user_id'].nunique())

        st.subheader("Activity by Group")
        fig = px.bar(df['group_name'].value_counts(), labels={'value':'Messages', 'index':'Group'})
        st.plotly_chart(fig)

        st.subheader("Recent Activity Logs")
        st.dataframe(df.tail(10))
    else:
        st.info("No data found! Start 'spy_core.py' and let the bot track some group messages.")
except Exception:
    st.error("Database (spy_pro_data.db) not found or not ready!")