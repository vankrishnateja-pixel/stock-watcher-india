import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FinQuest Pro | Indian Stock Watcher",
    page_icon="📈",
    layout="wide"
)

# --- 2. PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #0077B5; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
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

# --- 4. NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("💎 FinQuest Navigation")
    menu = st.radio("Go to:", ["Market Intelligence", "SIP Architect", "About"])
    st.markdown("---")
    st.caption("Data: 15-min delayed NSE")

# --- 5. MARKET INTELLIGENCE TAB ---
if menu == "Market Intelligence":
    st.header("🚀 Market Intelligence")
    
    ticker_input = st.text_input("Enter NSE Ticker (e.g., RELIANCE, TCS, ZOMATO)", "RELIANCE").upper()
    ticker = f"{ticker_input}.NS"
    
    # Fetch Data
    with st.spinner(f"Loading {ticker_input} data..."):
        data = yf.download(ticker, period="1y", interval="1d", progress=False)

    # ERROR HANDLING: Check if data exists
    if data.empty or len(data) < 2:
        st.error(f"❌ Error: Could not find data for '{ticker_input}'. Please ensure it is a valid NSE symbol.")
    else:
        # FIXING THE TYPEERROR: Extracting single values correctly
        current_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2])
        day_high = float(data['High'].iloc[-1])
        day_low = float(data['Low'].iloc[-1])
        change = current_close - prev_close
        pct_change = (change / prev_close) * 100

        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("LTP", f"₹{current_close:,.2f}", f"{pct_change:.2f}%")
        col2.metric("24h High", f"₹{day_high:,.2f}")
        col3.metric("24h Low", f"₹{day_low:,.2f}")
        col4.metric("52W High", f"₹{data['High'].max():,.2f}")

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

# --- 6. SIP ARCHITECT TAB ---
elif menu == "SIP Architect":
    st.header("🎯 Wealth Architect")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        monthly_investment = st.slider("Monthly SIP (₹)", 500, 200000, 10000, step=500)
        tenure_years = st.slider("Tenure (Years)", 1, 40, 15)
        return_rate = st.slider("Expected Annual Return (%)", 5, 25, 12)

    # SIP Formula
    i = (return_rate / 100) / 12
    n = tenure_years * 12
    future_value = monthly_investment * (((1 + i)**n - 1) / i) * (1 + i)
    total_invested = monthly_investment * n
    wealth_gained = future_value - total_invested

    with c2:
        st.subheader("Results")
        st.metric("Future Value", f"₹{future_value:,.0f}")
        st.write(f"💼 **Total Invested:** ₹{total_invested:,.0f}")
        st.write(f"📈 **Wealth Gained:** ₹{wealth_gained:,.0f}")
        
        # Simple Visualization
        chart_data = pd.DataFrame({
            "Category": ["Invested", "Gains"],
            "Amount": [total_invested, wealth_gained]
        })
        st.bar_chart(chart_data.set_index("Category"))

# --- 7. ABOUT TAB ---
elif menu == "About":
    st.header("ℹ️ Project Info")
    st.write("""
    This app was built for educational purposes to demonstrate how to track 
    Indian Stock Market trends with a 15-minute delay.
    
    **Features:**
    - Live-ish data using Yahoo Finance API
    - Professional-grade Candlestick charting
    - Mathematical SIP projection tools
    - Secure access key protection
    """)