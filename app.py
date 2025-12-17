import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. APPLE STOCKS DESIGN (CSS) ---
st.set_page_config(page_title="Stocks", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    /* Clean Apple-style Background */
    .stApp { background-color: #000000; color: white; }
    
    /* Sidebar Watchlist Styling */
    section[data-testid="stSidebar"] {
        background-color: #1c1c1e !important;
        border-right: 1px solid #38383a;
        width: 300px !important;
    }
    
    /* Metric Styling */
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 700 !important; color: white !important; }
    [data-testid="stMetricDelta"] { font-size: 18px !important; }
    
    /* Button Styling to look like list items */
    .stButton>button {
        width: 100%;
        background-color: transparent;
        color: white;
        border: none;
        border-bottom: 1px solid #38383a;
        text-align: left;
        padding: 15px 10px;
        border-radius: 0;
    }
    .stButton>button:hover { background-color: #2c2c2e; border-bottom: 1px solid #38383a; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE"

# --- 3. SIDEBAR WATCHLIST ---
with st.sidebar:
    st.title("Stocks")
    search = st.text_input("", placeholder="Search Tickers", label_visibility="collapsed").upper()
    if search:
        if st.button(f"🔍 Search: {search}"):
            st.session_state.selected_ticker = search

    st.markdown("---")
    
    # Pre-defined Apple-style Watchlist
    watchlist = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ZOMATO", "TATAMOTORS", "ICICIBANK"]
    
    for stock in watchlist:
        if st.button(f"**{stock}**", key=f"list_{stock}"):
            st.session_state.selected_ticker = stock

# --- 4. MAIN DISPLAY (APPLE STOCKS LAYOUT) ---
ticker = st.session_state.selected_ticker
data = yf.download(f"{ticker}.NS", period="1d", interval="1m", progress=False)

if not data.empty:
    # Flatten columns
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    
    ltp = float(data['Close'].iloc[-1])
    prev_close = float(data['Open'].iloc[0]) # Start of day
    change = ltp - prev_close
    pct_change = (change / prev_close) * 100
    
    # Header Section
    st.title(ticker)
    st.subheader("National Stock Exchange")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.metric(label="", value=f"₹{ltp:,.2f}", delta=f"{change:+.2f} ({pct_change:+.2f}%)")
    
    # 5. THE CHART (CLEAN APPLE TRENDLINE)
    # Apple uses a clean line chart with a gradient fill
    fig = go.Figure()
    
    # Choose color based on gain/loss
    line_color = "#30d158" if change >= 0 else "#ff453a" # Apple Green/Red
    
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['Close'], 
        mode='lines',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba({48 if change >= 0 else 255}, {209 if change >= 0 else 69}, {88 if change >= 0 else 58}, 0.1)',
        name="Price"
    ))

    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(showgrid=False, showticklabels=True, color="#8e8e93"),
        yaxis=dict(side="right", showgrid=True, gridcolor="#2c2c2e", color="#8e8e93"),
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 6. ALERT & INFO SECTION
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔔 Price Alert")
        target = st.number_input("Target Price", value=round(ltp, 2))
        email = st.text_input("Email ID", placeholder="Enter email for alerts")
        if st.button("Set Alert"):
            st.success(f"Alert set for {ticker} at ₹{target}")
            if ltp <= target:
                st.toast("🎯 Target Reached!", icon="✅")
    
    with c2:
        st.markdown("### 📊 Market Stats")
        st.write(f"**Open:** ₹{data['Open'].iloc[0]:,.2f}")
        st.write(f"**High:** ₹{data['High'].max():,.2f}")
        st.write(f"**Low:** ₹{data['Low'].min():,.2f}")
        st.write(f"**Vol:** {data['Volume'].iloc[-1]:,.0f}")

else:
    st.error("Ticker not found. Please ensure it's a valid NSE code.")