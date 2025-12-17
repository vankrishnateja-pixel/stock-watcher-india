import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIG & STYLING (Hides all raw code) ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sleek Landing Page Buttons */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em; font-size: 1.1em;
        background-color: #1C1C1E; border: 1px solid #38383a; color: white;
    }
    .stButton>button:active { transform: scale(0.98); }
    
    /* Card Styles */
    .market-card {
        background: rgba(28, 28, 30, 0.8); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION LOGIC ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "ticker" not in st.session_state:
    st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker:
        st.session_state.ticker = ticker
    st.rerun()

# --- 3. PAGE: LANDING ---
if st.session_state.page == "home":
    st.title("FinQuest Pro")
    st.markdown("### Welcome to the future of finance.")
    st.write("I am **Krishna**, the creator of FinQuest Pro. This terminal is built to bring professional-grade market insights to your mobile device with a clean, distraction-free experience.")
    
    st.markdown("---")
    st.subheader("Global Markets")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Top Global Stocks"): nav("global")
        if st.button("🇺🇸 S&P 500 Index"): nav("sp500")
    with col2:
        if st.button("🇮🇳 Nifty 50 Index"): nav("nifty")
        if st.button("📉 Sensex India"): nav("sensex")

# --- 4. PAGE: MARKET LISTS ---
elif st.session_state.page in ["global", "nifty", "sp500", "sensex"]:
    if st.button("← Back to Home"): nav("home")
    
    lists = {
        "global": ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL"],
        "nifty": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ZOMATO.NS"],
        "sp500": ["AMZN", "META", "UNH", "JPM"],
        "sensex": ["ITC.NS", "SBIN.NS", "ICICIBANK.NS", "LT.NS"]
    }
    
    selected_list = lists[st.session_state.page]
    st.title(f"{st.session_state.page.upper()} Watchlist")
    
    for t in selected_list:
        if st.button(f"Analyze {t}", key=f"btn_{t}"):
            nav("detail", t)

# --- 5. PAGE: STOCK DETAIL (Including Financials Chart) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back to List"): nav("home")
    
    stock = yf.Ticker(t)
    st.title(f"Analysis: {t}")
    
    # Financials Chart
    st.subheader("📊 Financial Growth")
    
    try:
        fin_df = stock.financials.T
        if not fin_df.empty and 'Total Revenue' in fin_df.columns:
            # Prepare data for plotting
            plot_df = fin_df[['Total Revenue', 'Net Income']].head(4)
            fig_fin = px.bar(
                plot_df, barmode='group', 
                template="plotly_dark",
                color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'}
            )
            fig_fin.update_layout(
                plot_bgcolor="black", 
                paper_bgcolor="black", 
                height=350,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_fin, width='stretch')
        else:
            st.info("Annual financials are currently private or unavailable for this ticker.")
    except Exception:
        st.error("Could not load financial statements for this ticker.")
        
    # Price Summary
    st.markdown("---")
    info = stock.info
    c1, c2 = st.columns(2)
    c1.metric("Market Cap", f"₹{info.get('marketCap', 0)/1e12:.2f}T")
    c2.metric("PE Ratio", f"{info.get('trailingPE', 'N/A')}")