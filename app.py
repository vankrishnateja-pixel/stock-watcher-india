import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIG & APP STYLING ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Personal Intro Styling */
    .intro-card {
        background: linear-gradient(135deg, #1c1c1e 0%, #000000 100%);
        border: 1px solid #38383a;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        text-align: center;
    }
    
    /* Button & Table Styling */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #1C1C1E; border: 1px solid #38383a; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & DATA ENGINE ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

def get_market_summary():
    # Fetching major indices for the Home Bar Chart
    indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Sensex": "^BSESN"}
    data = []
    for name, sym in indices.items():
        try:
            val = yf.download(sym, period="1d", progress=False)['Close'].iloc[-1]
            data.append({"Index": name, "Value": val})
        except: pass
    return pd.DataFrame(data)

# --- 3. PAGE: HOME SCREEN (Introduction & Global Financials) ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="intro-card">
            <h1 style='color: #007aff; margin-bottom:0;'>Krishna</h1>
            <p style='font-size: 1.2em; color: #8e8e93;'>Creator of FinQuest Pro</p>
            <p style='max-width: 600px; margin: 0 auto;'>Welcome to your personal financial terminal. 
            I built this app to simplify complex market data into actionable insights for the modern investor.</p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Global Market Snapshot")
    summary_df = get_market_summary()
    if not summary_df.empty:
        fig_home = px.bar(summary_df, x='Index', y='Value', color='Index', 
                          template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_home.update_layout(plot_bgcolor="black", paper_bgcolor="black", showlegend=False)
        st.plotly_chart(fig_home, use_container_width=True)

    st.markdown("---")
    st.write("🔍 **Quick Navigation**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇮🇳 Nifty 50 Leaders"): nav("nifty")
    with col2:
        query = st.text_input("", placeholder="Search Ticker (e.g. AAPL)...", key="search_home")
        if query: nav("detail", query.upper())

# --- 4. PAGE: NIFTY 50 TABLE ---
elif st.session_state.page == "nifty":
    st.title("🇮🇳 Nifty 50 - Top 10 Stocks")
    if st.button("← Back to Home"): nav("home")
    
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
               "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS"]
    
    # Simple table display
    prices = []
    for t in tickers:
        try:
            p = yf.download(t, period="1d", progress=False)['Close'].iloc[-1]
            prices.append({"Symbol": t.replace(".NS", ""), "Price": f"₹{p:,.2f}"})
        except: pass
    
    st.table(pd.DataFrame(prices))
    
    st.write("---")
    st.write("Select a stock for deep analysis:")
    cols = st.columns(2)
    for i, t in enumerate(tickers):
        with cols[i % 2]:
            if st.button(f"Analyze {t.split('.')[0]}", key=f"btn_{t}"):
                nav("detail", t)

# --- 5. PAGE: DETAIL ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back"): nav("home")
    st.header(f"Terminal: {t}")
    # ... (Trend line and Financials code from previous step)