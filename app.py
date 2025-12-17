import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PREMIUM DARK UI ---
st.set_page_config(page_title="FinQuest Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    section[data-testid="stSidebar"] { background-color: #1c1c1e !important; border-right: 1px solid #38383a; width: 350px !important; }
    .stMetric { background-color: #1c1c1e; border-radius: 10px; padding: 15px; border: 1px solid #38383a; }
    [data-testid="stMetricValue"] { color: white !important; font-size: 28px !important; }
    .stButton>button { width: 100%; background-color: transparent; color: white; border: none; border-bottom: 1px solid #38383a; text-align: left; padding: 15px 10px; }
    .stButton>button:hover { background-color: #2c2c2e; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE & SEARCH ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"

def search_stocks(query):
    try:
        search = yf.Search(query, max_results=5)
        return [{"symbol": q['symbol'], "display": f"{q['symbol']} - {q.get('shortname', '')}"} for q in search.quotes]
    except: return []

# --- 3. SIDEBAR (Watchlist & Heatmap) ---
with st.sidebar:
    st.title("FinQuest Pro")
    
    sq = st.text_input("Search", placeholder="Company or Ticker...")
    if sq:
        results = search_stocks(sq)
        for r in results:
            if st.button(r['display'], key=f"search_{r['symbol']}"):
                st.session_state.selected_ticker = r['symbol']

    st.markdown("### 🔥 Market Heatmap")
    # Added error handling for heatmap indices
    indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Nasdaq": "^IXIC"}
    for name, sym in indices.items():
        idx_data = yf.Ticker(sym).history(period="5d") # Increased period for safety
        if len(idx_data) >= 2:
            current_close = idx_data['Close'].iloc[-1]
            prev_close = idx_data['Close'].iloc[-2]
            change = ((current_close / prev_close) - 1) * 100
            color = "#30d158" if change >= 0 else "#ff453a"
            st.markdown(f"{name} <span style='color:{color}; float:right;'>{change:+.2f}%</span>", unsafe_allow_html=True)
        else:
            st.caption(f"{name} Data Unavailable")

    st.markdown("---")
    st.subheader("My Watchlist")
    for s in ["RELIANCE.NS", "TCS.NS", "AAPL", "NVDA", "TSLA", "ZOMATO.NS"]:
        if st.button(f"**{s}**"): st.session_state.selected_ticker = s

# --- 4. MAIN DASHBOARD ---
ticker = st.session_state.selected_ticker
stock = yf.Ticker(ticker)

# Fetching Data with safety check
data = stock.history(period="1y", interval="1d")

if not data.empty and len(data) >= 2:
    # Fix for Multi-Index columns in newer yfinance versions
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    info = stock.info
    ltp = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2]
    change = ltp - prev_close
    pct = (change / prev_close) * 100

    # Header Row
    st.title(info.get('longName', ticker))
    c1, c2, c3 = st.columns([2, 1, 1])
    
    # UI FIX: Added labels to metrics for accessibility/errors
    c1.metric("Current Price", f"{info.get('currency', '₹')}{ltp:,.2f}", f"{pct:+.2f}%")
    
    # RSI calculation for sentiment
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi_val = 100 - (100 / (1 + (gain/loss))).iloc[-1]
    
    sentiment = "Bullish 🚀" if rsi_val > 55 else "Bearish 📉" if rsi_val < 45 else "Neutral ⚖️"
    c2.metric("Market Sentiment", sentiment, f"RSI: {rsi_val:.1f}")

    # --- 5. THE CHART ---
    res = st.segmented_control("Select Range", options=["1D", "1M", "1Y", "5Y"], default="1Y")
    
    # FIX: 1D charts need valid intervals (1m or 2m)
    chart_interval = "2m" if res == "1D" else "1d"
    chart_data = stock.history(period=res.lower(), interval=chart_interval)
    
    if not chart_data.empty:
        if isinstance(chart_data.columns, pd.MultiIndex):
            chart_data.columns = chart_data.columns.get_level_values(0)
            
        fig = go.Figure()
        line_color = "#30d158" if pct >= 0 else "#ff453a"
        fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'], mode='lines', 
                                 line=dict(color=line_color, width=3), fill='tozeroy',
                                 fillcolor=f"rgba({(48 if pct >= 0 else 255)}, {(209 if pct >= 0 else 69)}, {(88 if pct >= 0 else 58)}, 0.1)"))
        fig.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", 
                          height=400, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right"))
        
        # UI FIX: Replaced use_container_width with width='stretch' for 2025 compliance
        st.plotly_chart(fig, width='stretch')

    # --- 6. FUNDAMENTALS ---
    st.markdown("### 📊 Financial Overview")
    try:
        # Simple data points for a professional look
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Day High", f"₹{data['High'].iloc[-1]:,.2f}")
        m2.metric("Day Low", f"₹{data['Low'].iloc[-1]:,.2f}")
        m3.metric("52W High", f"₹{info.get('fiftyTwoWeekHigh', 0):,.2f}")
        m4.metric("Market Cap", f"{info.get('marketCap', 0)/1e12:.2f}T")
    except:
        st.info("Additional market data currently unavailable.")

else:
    st.error(f"⚠️ No data found for {ticker}. The ticker might be delisted or the market is currently closed with no data.")