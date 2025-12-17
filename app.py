import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FinQuest Pro | NSE Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- 2. AUTHENTICATION ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 FinQuest Pro Access")
    password = st.text_input("Enter Access Key", type="password")
    if st.button("Unlock Dashboard"):
        if password == "invest2025":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid Key. Hint: invest2025")
    st.stop()

# --- 3. NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("💎 Navigation")
    menu = st.radio("Go to:", ["Market Intelligence", "SIP Architect", "About"])
    st.markdown("---")
    st.caption("Data: 15-min delayed NSE")

# --- 4. MARKET INTELLIGENCE TAB ---
if menu == "Market Intelligence":
    st.header("🚀 Market Intelligence")
    
    ticker_input = st.text_input("Enter NSE Ticker (e.g., RELIANCE, TCS)", "RELIANCE").upper()
    ticker = f"{ticker_input}.NS"
    
    with st.spinner(f"Fetching {ticker_input}..."):
        # Added auto_adjust=True to fix the FutureWarning
        data = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)

    if data.empty or len(data) < 2:
        st.error(f"❌ No data found for '{ticker_input}'.")
    else:
        # FIXING THE TYPEERROR & FUTUREWARNINGS
        # We use .iloc[-1] and then .item() to ensure we get a plain Python float
        current_close = float(data['Close'].iloc[-1].item())
        prev_close = float(data['Close'].iloc[-2].item())
        day_high = float(data['High'].iloc[-1].item())
        day_low = float(data['Low'].iloc[-1].item())
        
        # Calculate 52W High safely
        high_52w = float(data['High'].max().item())
        
        change = current_close - prev_close
        pct_change = (change / prev_close) * 100

        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("LTP", f"₹{current_close:,.2f}", f"{pct_change:.2f}%")
        col2.metric("24h High", f"₹{day_high:,.2f}")
        col3.metric("24h Low", f"₹{day_low:,.2f}")
        col4.metric("52W High", f"₹{high_52w:,.2f}")

        # Advanced Charting
        st.subheader(f"📈 {ticker_input} Price Trend")
        fig = go.Figure(data=[go.Candlestick(
            x=data.index[-90:],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Price"
        )])
        fig.update_layout(
            template="plotly_white",
            height=500,
            xaxis_rangeslider_visible=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# --- 5. SIP ARCHITECT TAB ---
elif menu == "SIP Architect":
    st.header("🎯 Wealth Architect")
    c1, c2 = st.columns([1, 1])
    with c1:
        monthly = st.slider("Monthly SIP (₹)", 500, 200000, 10000, step=500)
        years = st.slider("Tenure (Years)", 1, 40, 15)
        rate = st.slider("Expected Return (%)", 5, 25, 12)

    i = (rate / 100) / 12
    n = years * 12
    fv = monthly * (((1 + i)**n - 1) / i) * (1 + i)
    
    with c2:
        st.subheader("Results")
        st.metric("Future Value", f"₹{fv:,.0f}")
        st.info(f"Total Invested: ₹{monthly*n:,.0f} | Gains: ₹{fv - (monthly*n):,.0f}")

# --- 6. ABOUT TAB ---
elif menu == "About":
    st.header("ℹ️ Project Info")
    st.write("Professional Stock Watcher for NSE India. Built with Python & Streamlit.")