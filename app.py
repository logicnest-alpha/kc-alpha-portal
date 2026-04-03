import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. SETUP & THEME
st.set_page_config(page_title="Syndicate OS", page_icon="🛡️", layout="wide")

# 2. LOGIN SYSTEM
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ SYNDICATE LOGIN")
    user_input = st.text_input("Client ID")
    pw_input = st.text_input("Access Key", type="password")
    
    if st.button("Unlock Portal"):
        # This checks the [credentials] section in your secrets
        if user_input in st.secrets["credentials"] and pw_input == st.secrets["credentials"][user_input]:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.rerun()
        else:
            st.error("Access Denied: Invalid Credentials")
    st.stop()

# 3. LOGGED IN AREA
st.sidebar.title(f"Client: {st.session_state.user}")
page = st.sidebar.radio("Navigation", ["Performance", "Lead Data"])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# 4. DATA ENGINE
conn = st.connection("gsheets", type=GSheetsConnection)

if page == "Performance":
    st.title("📊 Ads Performance (Manual)")
    try:
        # Pulls from the 'AdsPerformance' tab
        df = conn.read(worksheet="AdsPerformance", ttl=0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Spend", f"₹{df['Spend'].sum():,.2f}")
        c2.metric("Avg CTR", f"{df['CTR'].mean():.2f}%")
        c3.metric("Total Clicks", f"{int(df['Clicks'].sum()):,}")
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    except:
        st.warning("Please ensure your Google Sheet has a tab named 'AdsPerformance'")

elif page == "Lead Data":
    st.title("📂 Prospect Database")
    try:
        # Pulls from the 'Leads' tab
        leads = conn.read(worksheet="Leads", ttl=0)
        st.dataframe(leads, use_container_width=True, hide_index=True)
    except:
        st.warning("Please ensure your Google Sheet has a tab named 'Leads'")