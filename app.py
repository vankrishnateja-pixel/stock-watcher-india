import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="FinQuest Terminal Pro", layout="wide", page_icon="📈")

# Custom CSS for a clean, dark-themed professional look
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Terminal Access")
    key = st.text_input("Enter Access Key", type="password")
    if st.button("Initialize"):
        if key == "invest2025":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. INDUSTRY DIRECTORY ---
st.title("📟 Market Intelligence Terminal")

with st.expander("📂 Industry Directory (Select a Stock to View Profile)", expanded=True):
    industry_map = {
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN"],
        "IT Services": ["TCS", "INFY", "WIPRO"],
        "Energy": ["RELIANCE", "ONGC", "BPCL"],
        "Consumer": ["HINDUNILVR", "ITC", "TATACONSUM"],
        "Automobile": ["TATAMOTORS", "M&M", "MARUTI"]
    }
    
    # Create columns for a tabular look
    cols = st.columns(len(industry_map))
    selected_stock = st.session_state.get("current_ticker", "RELIANCE")

    for i, (industry, stocks) in enumerate(industry_map.items()):
        with cols[i]:
            st.markdown(f"**{industry}**")
            for s in stocks:
                if st.button(f"view {s}", key=f"btn_{s}"):
                    st.session_state.current_ticker = s
                    st.rerun()

st.divider()

# --- 4. INDIVIDUAL STOCK PROFILE ---
ticker_to_load = st.session_state.get("current_ticker", "RELIANCE")
st.header(f"📊 Stock Profile: {ticker_to_load}")

# Timeframe Selector
timeframe = st.segmented_control("Select Timeframe", options=["1mo", "6mo", "1y", "5y"], default="1y")

# Fetch Data
ticker_ns = f"{ticker_to_load}.NS"
data = yf.download(ticker_ns, period=timeframe, interval="1d", auto_adjust=True)

if not data.empty:
    # Calculations
    ltp = data['Close'].iloc[-1].item()
    prev_close = data['Close'].iloc[-2].item()
    change_pct = ((ltp - prev_close) / prev_close) * 100
    
    # Technical: RSI for Buying Suggestions
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1].item()

    # Insight Logic
    if current_rsi < 30: insight, color = "PROBABLE BUY (Oversold)", "green"
    elif current_rsi > 70: insight, color = "PROBABLE SELL (Overbought)", "red"
    else: insight, color = "HOLD / NEUTRAL", "gray"

    # Display Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Price", f"₹{ltp:,.2f}", f"{change_pct:.2f}%")
    m2.metric("RSI (14-Day)", f"{current_rsi:.1f}")
    m3.markdown(f"**Buying Period Suggestion:** <br><h3 style='color:{color}; margin:0;'>{insight}</h3>", unsafe_allow_html=True)

    # --- 5. IMPROVED TREND LINE CHART ---
    st.subheader("Historical Trend Line")
    
    fig = go.Figure()
    # Adding a filled area under the line for better visibility
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['Close'], 
        mode='lines',
        line=dict(color='#1f77b4', width=3), # Bold line
        fill='tozeroy', # Shaded area below the line
        fillcolor='rgba(31, 119, 180, 0.1)', # Very light blue shade
        name="Close Price"
    ))

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(showgrid=False, title="Date"),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', title="Price (₹)"),
        margin=dict(l=0, r=0, t=10, b=0),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Ticker data not available. Please try a different symbol.")
    