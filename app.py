import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="FinQuest Terminal", layout="wide", page_icon="📈")

# Professional Styling: Removing padding and centering metrics
st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 15px; border-radius: 8px; border: 1px solid #eee; text-align: center; }
    .stTable { font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 FinQuest Terminal Access")
    key = st.text_input("Access Key", type="password")
    if st.button("Initialize Terminal"):
        if key == "invest2025":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📟 Terminal Menu")
    menu = st.radio("Switch View", ["Market Watcher", "SIP Planner"])
    st.markdown("---")
    st.caption("Status: Connected to NSE (15m Delay)")

# --- 4. MARKET WATCHER ---
if menu == "Market Watcher":
    st.header("🏢 Industry Snapshot")
    
    # 1. Industry Split in Tabular Structure
    industry_data = [
        {"Industry": "Banking", "Top Stocks": "HDFCBANK, ICICIBANK, SBIN"},
        {"Industry": "IT Services", "Top Stocks": "TCS, INFY, WIPRO"},
        {"Industry": "Energy", "Top Stocks": "RELIANCE, ONGC, BPCL"},
        {"Industry": "Consumer", "Top Stocks": "HINDUNILVR, ITC, TATACONSUM"},
        {"Industry": "Automobile", "Top Stocks": "TATAMOTORS, M&M, MARUTI"}
    ]
    st.table(pd.DataFrame(industry_data))

    st.markdown("---")
    
    # 2. Search and Intelligence
    col_search, col_time = st.columns([2, 1])
    ticker_input = col_search.text_input("Enter Ticker to Analyze", "RELIANCE").upper()
    timeframe = col_time.selectbox("History", ["1mo", "6mo", "1y", "2y"], index=2)
    
    ticker = f"{ticker_input}.NS"
    data = yf.download(ticker, period=timeframe, interval="1d", auto_adjust=True)

    if not data.empty:
        # Technical Logic (RSI)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1].item()

        # Suggestion Logic
        if current_rsi < 35:
            status, color = "GOOD TIME TO BUY (Oversold)", "green"
        elif current_rsi > 70:
            status, color = "HIGH RISK (Overbought)", "red"
        else:
            status, color = "NEUTRAL (Fair Value)", "orange"

        # KPIs
        ltp = data['Close'].iloc[-1].item()
        change = ((ltp / data['Close'].iloc[-2].item()) - 1) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Price", f"₹{ltp:,.2f}", f"{change:.2f}%")
        c2.metric("RSI Level", f"{current_rsi:.1f}")
        c3.markdown(f"**Buying Insight:** <br><span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)

        # 3. Clean Line Chart (No dots/values)
        st.subheader(f"Historical Trend: {ticker_input}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Close'], 
            mode='lines', # Strict line mode
            line=dict(color='#0077B5', width=2),
            name="Closing Price"
        ))
        fig.update_layout(
            template="plotly_white",
            height=400,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Invalid Ticker. Please use standard NSE codes.")

# --- 5. SIP PLANNER ---
else:
    st.header("🎯 Capital Growth Planner")
    # ... (Standard SIP Logic kept clean)
    amt = st.number_input("Monthly Contribution (₹)", 5000)
    yrs = st.slider("Duration (Years)", 1, 30, 10)
    # Simple calculation display
    fv = amt * (((1 + 0.01)**(yrs*12) - 1) / 0.01) # 12% fixed for clean UI
    st.metric("Estimated Wealth", f"₹{fv:,.0f}")