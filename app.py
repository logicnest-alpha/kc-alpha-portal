import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import plotly.express as px

# 1. ALPHA UI ARCHITECTURE
st.set_page_config(page_title="KC Alpha | Syndicate OS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    /* Glassmorphism Cards */
    div[data-testid="column"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        padding: 25px !important;
        border-radius: 20px !important;
    }
    h1, h2, h3, p, span { color: #FFFFFF !important; font-family: 'Inter', sans-serif; }
    div[data-testid="stMetricValue"] { color: #38BDF8 !important; font-weight: 800; text-shadow: 0 0 10px rgba(56,189,248,0.3); }
    .stButton>button { background-color: #38BDF8; color: black; border-radius: 10px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. SECURITY GATEKEEPER
def check_auth():
    def login_attempt():
        # Validates against .streamlit/secrets.toml [credentials]
        if st.session_state["user"] in st.secrets["credentials"] and \
           st.session_state["pw"] == st.secrets["credentials"][st.session_state["user"]]:
            st.session_state["auth_active"] = True
        else:
            st.session_state["auth_active"] = False
            st.error("Invalid Intelligence Credentials")

    if "auth_active" not in st.session_state or not st.session_state["auth_active"]:
        st.markdown("<h1 style='text-align: center;'>🛡️ SYNDICATE LOGIN</h1>", unsafe_allow_html=True)
        st.text_input("Username", key="user", placeholder="Enter Client ID")
        st.text_input("Security Key", type="password", key="pw", placeholder="••••••••")
        st.button("Enter Secure Node", on_click=login_attempt)
        return False
    return True

# 3. ANALYTICS LOGIC
def get_insights(df):
    count = len(df)
    if count > 10:
        return "Synthesis: High-velocity lead flow detected. Recommend scaling architecture by 15%."
    return "Status: Initial calibration active. Maintaining current market synthesis."

# 4. DASHBOARD EXECUTION
if check_auth():
    # SYNC WITH MASTER WAREHOUSE
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # It pulls the URL automatically from .streamlit/secrets.toml
        master_df = conn.read(ttl=0)
        
        # --- THE SECURITY FILTER ---
        # Only grab rows where 'Client_Name' column matches the logged-in username
        current_user = st.session_state["user"]
        client_df = master_df[master_df['Client_Name'] == current_user].copy()
        client_df['Date'] = pd.to_datetime(client_df['Date'])
    except Exception as e:
        st.error(f"Engine Connection Error: {e}")
        st.stop()

    if not client_df.empty:
        # SIDEBAR CONTROL
        st.sidebar.markdown(f"<h2 style='color: #38BDF8;'>🛡️ {current_user.upper()}</h2>", unsafe_allow_html=True)
        st.sidebar.write("`STATUS: OPTIMIZED`")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        # DASHBOARD HEADER
        st.title("Executive Intelligence Portal")
        st.write("`NODE: SECURE` | `PIXEL: SERVER-SIDE` | `MARKET: AGGRESSIVE` ")

        # KPIS
        m1, m2, m3 = st.columns(3)
        m1.metric("Leads Synthesized", len(client_df))
        m2.metric("Market Dominance", "22.4%")
        m3.metric("Lead Temp", "88/100")

        st.markdown("---")

        # VISUAL SYNTHESIS
        left, right = st.columns([2, 1])
        with left:
            st.subheader("📈 Lead Generation Architecture")
            fig = px.area(client_df, x='Date', y='Ad_Spend', template="plotly_dark")
            fig.update_traces(line_color='#38BDF8', line_shape='spline', fillcolor="rgba(56, 189, 248, 0.05)")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with right:
            st.subheader("🛡️ Syndicate Insights")
            st.info(get_insights(client_df))
            st.caption("Proprietary Analytics Engine v5.0")
            
            # Donut Chart for Status
            if 'Status' in client_df.columns:
                fig_pie = px.pie(client_df, names='Status', hole=0.7, color_discrete_sequence=['#38BDF8', '#1E293B'])
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=200, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_pie, use_container_width=True)

        # DATA FEED
        st.subheader("📋 Proprietary Lead Feed (Scrubbed)")
        display_df = client_df.copy().sort_values('Date', ascending=False)
        # Visual Alpha: Add a random Heat Score
        display_df['Heat'] = [f"🔥 {np.random.randint(85, 99)}%" for _ in range(len(display_df))]
        st.dataframe(display_df[['Date', 'Lead_Name', 'Status', 'Heat']], use_container_width=True, hide_index=True)
    else:
        st.warning(f"Welcome {current_user}. Your account is being calibrated. Check back in 24 hours.")