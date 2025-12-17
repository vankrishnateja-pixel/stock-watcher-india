import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 FinQuest Pro Access")
    key = st.text_input("Access Key", type="password")
    if st.button("Unlock Dashboard"):
        if key == "invest2025":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. SIDEBAR NAVIGATION & MARKET PULSE ---
with st.sidebar:
    st.title("💎 FinQuest Pro")
    menu = st.radio("Navigation", ["Market Watcher", "SIP Architect"])
    
    st.markdown("---")
    st.subheader("🏢 Top Stocks by Industry")
    # Categorized Top 10 Stocks
    industries = {
        "IT": ["TCS", "INFY"],
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN"],
        "Energy/Oil": ["RELIANCE", "ONGC"],
        "Consumer": ["HINDUNILVR", "ITC"],
        "Auto": ["TATA MOTORS"]
    }
    
    for ind, stocks in industries.items():
        st.caption(f"**{ind}**")
        for s in stocks:
            if st.button(s, key=f"btn_{s}"):
                st.session_state.selected_ticker = s

# --- 4. MARKET WATCHER LOGIC ---
if menu == "Market Watcher":
    st.header("📈 Market Intelligence")
    
    # Check if a stock was clicked in sidebar, otherwise default to RELIANCE
    default_ticker = st.session_state.get("selected_ticker", "RELIANCE")
    ticker_input = st.text_input("Search NSE Ticker", value=default_ticker).upper()
    
    timeframe = st.selectbox("Select Historical View", ["1mo", "6mo", "1y", "5y"], index=2)
    
    # Fetch Data
    ticker = f"{ticker_input}.NS"
    data = yf.download(ticker, period=timeframe, interval="1d", auto_adjust=True)

    if data.empty:
        st.error("❌ Data not found. Ensure the ticker is correct (e.g., RELIANCE).")
    else:
        # Extract single values safely
        current_price = float(data['Close'].iloc[-1].item())
        prev_price = float(data['Close'].iloc[-2].item())
        change = current_price - prev_price
        pct_change = (change / prev_price) * 100

        # --- 5. BUYING PERIOD ANALYST (RSI Implementation) ---
        # Calculate RSI to suggest buying periods
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1].item()

        # Suggestion Logic
        if current_rsi < 35:
            advice = "🟢 **Strong Value Zone:** Stock is 'Oversold'. Good period to consider buying."
        elif current_rsi > 70:
            advice = "🔴 **Caution Zone:** Stock is 'Overbought'. High risk to buy now."
        else:
            advice = "🟡 **Neutral Zone:** Stock is trading at fair value. Wait for a dip or steady trend."

        # KPI Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("LTP", f"₹{current_price:,.2f}", f"{pct_change:.2f}%")
        c2.metric("Period High", f"₹{data['High'].max().item():,.2f}")
        c3.metric("RSI (14d)", f"{current_rsi:.1f}")
        
        st.info(advice)

        # --- 6. HISTORICAL GRAPH (Plotly) ---
        st.subheader(f"Historical Price Action: {ticker_input}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Close Price", line=dict(color='#0077B5', width=2)))
        fig.update_layout(template="plotly_white", height=450, xaxis_rangeslider_visible=True, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

# --- 7. SIP ARCHITECT ---
elif menu == "SIP Architect":
    st.header("🎯 Wealth Architect")
    col1, col2 = st.columns(2)
    with col1:
        amt = st.number_input("Monthly SIP (₹)", 500, 500000, 10000)
        yrs = st.slider("Years", 1, 40, 15)
        rate = st.slider("Return (%)", 5, 25, 12)
        
        i = (rate/100)/12
        n = yrs * 12
        fv = amt * (((1 + i)**n - 1) / i) * (1 + i)
        
    with col2:
        st.metric("Expected Corpus", f"₹{fv:,.0f}")
        st.write(f"Invested: ₹{amt*n:,.0f} | Profit: ₹{fv - (amt*n):,.0f}")