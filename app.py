import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="FinQuest Pro Terminal", layout="wide", page_icon="💹")

# State Management
if "auth" not in st.session_state: st.session_state.auth = False
if "watchlist" not in st.session_state: st.session_state.watchlist = []
if "page" not in st.session_state: st.session_state.page = "📊 Market Summary"
if "selected_stock" not in st.session_state: st.session_state.selected_stock = "RELIANCE"

# Professional Industry Data
industry_map = {
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
    "IT Services": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
    "Energy": ["RELIANCE", "ONGC", "BPCL", "NTPC", "POWERGRID"],
    "Consumer": ["HINDUNILVR", "ITC", "NESTLEIND", "TATACONSUM", "VBL"],
    "Automobile": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT"]
}

# --- 2. AUTHENTICATION ---
if not st.session_state.auth:
    st.title("🔐 FinQuest Pro Terminal")
    key = st.text_input("Access Key", type="password")
    if st.button("Initialize Terminal"):
        if key == "invest2025":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. UNIVERSAL DATA ENGINE ---
def fetch_safe_data(ticker_input, period="1y"):
    """Fetches data and flattens columns to prevent 'Empty Chart' errors."""
    ticker = f"{ticker_input}.NS"
    try:
        data = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if data.empty: return None
        # Flatten MultiIndex columns if they exist (Fix for 'Empty Lines')
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return None

def get_suggestion(rsi_value):
    if rsi_value < 35: return "🟢 STRONG BUY", "Stock is Oversold. High probability of rebound."
    elif rsi_value > 65: return "🔴 SELL / AVOID", "Stock is Overbought. Risk of correction is high."
    else: return "🟡 HOLD / NEUTRAL", "Stock is trading at fair value. Wait for clear trend."

# --- 4. NAVIGATION ---
with st.sidebar:
    st.title("📟 FinQuest Menu")
    nav = st.radio("Navigate", ["📊 Market Summary", "🏢 Industry Movers", "📈 Stock Profile", "⭐ My Watchlist"])
    st.session_state.page = nav
    st.divider()
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- PAGE 1: MARKET SUMMARY ---
if st.session_state.page == "📊 Market Summary":
    st.header("📊 Top Stocks Summary")
    st.write("Click a button below to view the individual stock profile.")
    
    for industry, stocks in industry_map.items():
        st.subheader(f"📂 {industry}")
        cols = st.columns(len(stocks))
        for i, s in enumerate(stocks):
            if cols[i].button(f"🔍 {s}", key=f"sum_{s}"):
                st.session_state.selected_stock = s
                st.session_state.page = "📈 Stock Profile"
                st.rerun()
    st.divider()
    st.caption("This page provides quick navigation to top movers.")

# --- PAGE 2: INDUSTRY MOVERS ---
elif st.session_state.page == "🏢 Industry Movers":
    st.header("🏢 Industry Movers Table")
    selected_ind = st.selectbox("Select Industry Sector", list(industry_map.keys()))
    
    stocks = industry_map[selected_ind]
    ind_data = []
    
    with st.spinner("Fetching Sector Data..."):
        for s in stocks:
            data = fetch_safe_data(s, period="5d")
            if data is not None:
                ltp = float(data['Close'].iloc[-1])
                change = ((ltp - float(data['Close'].iloc[-2])) / float(data['Close'].iloc[-2])) * 100
                ind_data.append({"Ticker": s, "LTP": f"₹{ltp:,.2f}", "Change%": f"{change:+.2f}%", "High": f"₹{data['High'].iloc[-1]:,.2f}", "Low": f"₹{data['Low'].iloc[-1]:,.2f}"})

    st.table(pd.DataFrame(ind_data))
    st.info("To view detailed graphs, go to 'Stock Profile' and search the ticker.")

# --- PAGE 3: STOCK PROFILE (THE 'GOOD' GRAPH) ---
elif st.session_state.page == "📈 Stock Profile":
    ticker = st.session_state.selected_stock
    
    col_a, col_b = st.columns([3, 1])
    with col_b:
        search = st.text_input("Search Custom Ticker", value=ticker).upper()
        if search != ticker:
            st.session_state.selected_stock = search
            st.rerun()
        
        if st.button("⭐ Add to Watchlist"):
            if ticker not in st.session_state.watchlist:
                st.session_state.watchlist.append(ticker)
                st.success("Added!")

    st.header(f"📈 {ticker} Technical Profile")
    
    data = fetch_safe_data(ticker, period="1y")
    
    if data is not None:
        # 1. TECHNICAL CALCULATIONS
        # RSI for suggestion
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        curr_rsi = rsi.iloc[-1]
        
        # 2. SUGGESTION BOX
        tag, desc = get_suggestion(curr_rsi)
        st.success(f"**AI SUGGESTION:** {tag} — {desc}")

        # 3. THE "GOOD" TREND GRAPH
        # We use a Scatter with Area Fill and a Moving Average (Trend Line)
        data['MA20'] = data['Close'].rolling(window=20).mean() # 20-Day Moving Average
        
        fig = go.Figure()
        
        # Area Chart for Price
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Close'],
            fill='tozeroy',
            mode='lines',
            line=dict(width=2, color='#17BECF'),
            fillcolor='rgba(23, 190, 207, 0.1)',
            name="Daily Close"
        ))
        
        # Bold Trend Line (Moving Average)
        fig.add_trace(go.Scatter(
            x=data.index, y=data['MA20'],
            mode='lines',
            line=dict(width=3, color='#FF4B4B', dash='dash'),
            name="20-Day Trend"
        ))

        fig.update_layout(
            template="plotly_white",
            height=550,
            hovermode="x unified",
            xaxis=dict(showgrid=False, rangeslider=dict(visible=True)),
            yaxis=dict(title="Price (₹)", showgrid=True, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("LTP", f"₹{data['Close'].iloc[-1]:,.2f}")
        m2.metric("52W High", f"₹{data['High'].max():,.2f}")
        m3.metric("RSI (14D)", f"{curr_rsi:.1f}")

    else:
        st.error("Could not load data. Check ticker name.")

# --- PAGE 4: WATCHLIST ---
elif st.session_state.page == "⭐ My Watchlist":
    st.header("⭐ My Watchlist")
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Go to Stock Profile to add stocks.")
    else:
        for s in st.session_state.watchlist:
            col_x, col_y = st.columns([4, 1])
            col_x.subheader(f"📍 {s}")
            if col_y.button(f"View {s}", key=f"watch_view_{s}"):
                st.session_state.selected_stock = s
                st.session_state.page = "📈 Stock Profile"
                st.rerun()
        if st.button("🗑️ Clear All"):
            st.session_state.watchlist = []
            st.rerun()