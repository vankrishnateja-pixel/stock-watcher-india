import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIG & UI STYLE ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Search Bar Styling */
    .stTextInput>div>div>input {
        background-color: #1c1c1e; color: white; border: 1px solid #38383a;
        border-radius: 12px; padding: 10px;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em; font-size: 1.1em;
        background-color: #1C1C1E; border: 1px solid #38383a; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL SEARCH & NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# SEARCH BAR - Appears on every screen
query = st.text_input("🔍 Search Ticker (e.g. TSLA, TCS.NS)", placeholder="Enter symbol...", key="global_search")
if query:
    if st.button(f"Go to {query.upper()}"):
        nav("detail", query.upper())

def get_clean_data(ticker, period="1y"):
    df = yf.download(ticker, period=period, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# --- 3. PAGE: LANDING ---
if st.session_state.page == "home":
    st.title("FinQuest Pro")
    st.write("I am **Krishna**, the creator of FinQuest Pro. Quick-access markets are below.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Global Stocks"): nav("global")
        if st.button("🇺🇸 S&P 500"): nav("sp500")
    with col2:
        if st.button("🇮🇳 Nifty 50"): nav("nifty")
        if st.button("📉 Sensex India"): nav("sensex")

# --- 4. PAGE: WATCHLISTS ---
elif st.session_state.page in ["global", "nifty", "sp500", "sensex"]:
    if st.button("← Back to Home"): nav("home")
    lists = {
        "global": ["AAPL", "NVDA", "TSLA"], "nifty": ["RELIANCE.NS", "TCS.NS", "INFY.NS"],
        "sp500": ["AMZN", "META", "JPM"], "sensex": ["ITC.NS", "SBIN.NS", "LT.NS"]
    }
    st.title(f"{st.session_state.page.upper()} Watchlist")
    for t in lists[st.session_state.page]:
        if st.button(f"Analyze {t}", key=f"btn_{t}"): nav("detail", t)

# --- 5. PAGE: STOCK DETAIL (CHART + FINANCIALS) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back"): nav("home")
    
    df = get_clean_data(t)
    if not df.empty:
        st.subheader(f"{t} Price Trend")
        change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
        line_color = "#30d158" if change >= 0 else "#ff453a"
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color=line_color, width=3), fill='tozeroy'))
        fig_trend.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_trend, width='stretch')

        st.markdown("---")
        st.subheader("📊 Financial Growth")
        try:
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_fin = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_fin.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_fin, width='stretch')
        except:
            st.info("Financials unavailable.")
    else:
        st.error(f"Ticker '{t}' not found. Please check the symbol.")