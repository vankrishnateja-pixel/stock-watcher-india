import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION & UI ---
st.set_page_config(page_title="FinQuest Pro | NSE Dashboard", layout="wide", page_icon="💎")

# Sidebar - Professional Branding
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/stock-share.png", width=80)
    st.title("FinQuest Pro")
    st.markdown("---")
    
    # Secure Access
    if "auth" not in st.session_state:
        st.session_state.auth = False
    
    if not st.session_state.auth:
        key = st.text_input("Access Key", type="password")
        if st.button("Unlock Dashboard"):
            if key == "invest2025":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Invalid Key")
        st.stop()

    menu = st.radio("Navigation", ["Market Watch", "Portfolio Tracker", "SIP Intel", "Screener"])

# --- DATA ENGINE ---
@st.cache_data(ttl=900) # 15-min cache to be efficient
def get_data(ticker):
    return yf.download(f"{ticker}.NS", period="1y", interval="1d")

# --- APP TABS ---
if menu == "Market Watch":
    st.subheader("🚀 Interactive Market Intelligence")
    ticker = st.text_input("Enter NSE Ticker", "TCS").upper()
    data = get_data(ticker)
    
    if not data.empty:
        # KPI Row
        ltp = data['Close'].iloc[-1]
        change = ltp - data['Close'].iloc[-2]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("LTP", f"₹{ltp:,.2f}", f"{ (change/ltp)*100:.2f}%")
        c2.metric("Day High", f"₹{data['High'].iloc[-1]:,.2f}")
        c3.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}")
        
        # Technical Indicators Logic
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        
        # Advanced Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(x=data.index[-90:],
                        open=data['Open'], high=data['High'],
                        low=data['Low'], close=data['Close'], name="Price")])
        fig.add_trace(go.Scatter(x=data.index[-90:], y=data['MA20'][-90:], name="20-Day MA", line=dict(color='orange')))
        fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

elif menu == "Portfolio Tracker":
    st.subheader("📁 Your Virtual Holdings")
    st.info("Log your buy price to track unrealized gains.")
    # Example table - in a real app, this would save to a database
    portfolio = pd.DataFrame({
        "Stock": ["RELIANCE", "INFY", "ZOMATO"],
        "Qty": [10, 50, 100],
        "Avg Cost": [2400, 1500, 120]
    })
    st.table(portfolio)

elif menu == "SIP Intel":
    st.subheader("🎯 Long-term Wealth Architect")
    col1, col2 = st.columns([1, 1])
    with col1:
        monthly = st.slider("Monthly SIP (₹)", 500, 200000, 10000)
        years = st.number_input("Tenure (Years)", 1, 40, 15)
        rate = st.slider("Expected Return (%)", 8, 24, 13)
    
    # SIP Math
    i = (rate/100)/12
    n = years * 12
    fv = monthly * (((1 + i)**n - 1) / i) * (1 + i)
    
    with col2:
        st.metric("Future Value", f"₹{fv:,.0f}")
        st.write(f"Total Invested: ₹{monthly*n:,.0f}")
        st.write(f"Gains: ₹{fv - (monthly*n):,.0f}")