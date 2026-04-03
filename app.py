import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from openai import OpenAI

# 1. PREMIUM PAGE CONFIGURATION
st.set_page_config(
    page_title="KC Alpha | Syndicate OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. WHITE-LABEL UI HACK (Hides Streamlit Branding)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .stAppDeployButton {display:none;}
            /* Custom Glassmorphism Card Style */
            .stMetric {
                background: rgba(255, 255, 255, 0.05);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. AUTHENTICATION LOGIC
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] in st.secrets["credentials"] and \
           st.session_state["password"] == st.secrets["credentials"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.title("🛡️ SYNDICATE LOGIN")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        st.info("Authorized Personnel Only. Logins are tracked.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show error + re-render inputs.
        st.error("❌ Invalid Credentials")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Log In", on_click=password_entered)
        return False
    else:
        # Password correct.
        return True

# 4. START APP IF AUTHENTICATED
if check_password():
    
    # --- DATA ENGINE ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="1m") # Auto-refresh every minute

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title("KC ALPHA")
    st.sidebar.image("https://img.icons8.com/ios-filled/100/ffffff/shield.png", width=100)
    page = st.sidebar.radio("Navigation", ["Executive Dashboard", "AI Command Center", "Lead Database"])

    # --- PAGE 1: EXECUTIVE DASHBOARD ---
    if page == "Executive Dashboard":
        st.title("📈 Executive Intelligence")
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        total_leads = len(df)
        ad_spend = df['Ad_Spend'].sum() if 'Ad_Spend' in df.columns else 0
        cpl = ad_spend / total_leads if total_leads > 0 else 0
        
        m1.metric("Total Alpha Leads", total_leads)
        m2.metric("Total Ad Spend", f"₹{ad_spend:,}")
        m3.metric("Cost Per Lead", f"₹{cpl:.2f}")

        # Charts
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.area(df, x="Date", y="Ad_Spend", title="Spending Velocity", color_discrete_sequence=['#00D4FF'])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.pie(df, names="Status", title="Lead Pipeline Health", hole=0.5)
            st.plotly_chart(fig2, use_container_width=True)

    # --- PAGE 2: AI COMMAND CENTER (GROK INTEGRATION) ---
    elif page == "AI Command Center":
        st.title("🤖 Agentic Command Center")
        st.subheader("Powered by Grok-Beta")

        # Initialize Grok
        client = OpenAI(api_key=st.secrets["GROK_API_KEY"], base_url="https://api.x.ai/v1")

        selected_lead = st.selectbox("Select a Lead to Process", df['Lead_Name'].unique())
        
        if st.button("Analyze with Agent Alpha"):
            lead_data = df[df['Lead_Name'] == selected_lead].iloc[0]
            
            with st.status("Agent Alpha is analyzing...", expanded=True) as status:
                st.write("🔍 Extracting lead metadata...")
                st.write("🧠 Consulting Grok Knowledge Base...")
                
                prompt = f"Analyze this lead: {selected_lead}. Details: {lead_data.to_dict()}. " \
                         f"Give a score 1-10 and draft a personalized high-ticket pitch."
                
                response = client.chat.completions.create(
                    model="grok-beta",
                    messages=[{"role": "system", "content": "You are a witty, high-ticket sales closer."},
                              {"role": "user", "content": prompt}]
                )
                analysis = response.choices[0].message.content
                st.write("✅ Strategy Ready.")
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            st.chat_message("assistant").write(analysis)

    # --- PAGE 3: LEAD DATABASE ---
    elif page == "Lead Database":
        st.title("📂 Lead Archive")
        st.dataframe(df, use_container_width=True)
        
        if st.button("Force Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()