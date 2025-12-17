import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="FinQuest Pro Terminal", layout="wide", page_icon="💹")

# Initialize persistent data
if "auth" not in st.session_state: st.session_state.auth = False
if "watchlist" not in st.session_state: st.session_state.watchlist = []
if "page" not in st.session_state: st.session_state.page = "Summary"
if "selected_stock" not in st.session_state: st.session_state.selected_stock = "RELIANCE"

# Industry Data Mapping
industry_map = {
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
    "IT Services": ["TCS", "INFY", "WIPRO", "HCLTECH", "TECHM"],
    "Energy": ["RELIANCE", "ONGC", "BPCL", "NTPC", "POWERGRID"],
    "Consumer": ["HINDUNILVR", "ITC", "NESTLEIND", "TATACONSUM", "VBL"],
    "Automobile": ["TATAMOTORS", "M&M", "MARUTI", "BAJAJ-AUTO", "EICHERMOT"]
}
all_stocks = [s for sub in industry_map.values() for s in sub]

# --- 2. AUTHENTICATION ---
if not st.session_state.auth:
    st.title("🔐 FinQuest Pro Terminal")
    key = st.text_input("Access Key", type="password")
    if st.button("Initialize Terminal"):
        if key == "invest2025":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("💎 FinQuest Menu")
    nav = st.radio("Navigate", ["📊 Market Summary", "🏢 Industry Movers", "📈 Stock Profile", "⭐ My Watchlist"])
    st.session_state.page = nav
    st.divider()
    st.caption("Data: 15m Delayed NSE")

# Helper function to get single stock data row
def get_stock_stats(ticker):
    t = yf.Ticker(f"{ticker}.NS")
    hist = t.history(period="2d")
    if len(hist) < 2: return None
    ltp = hist['Close'].iloc[-1]
    prev = hist['Close'].iloc[-2]
    high = hist['High'].max()
    low = hist['Low'].min()
    vol = hist['Volume'].iloc[-1]
    change = ((ltp - prev)/prev)*100
    return {"Ticker": ticker, "LTP": ltp, "Change %": round(change, 2), "High": high, "Low": low, "Volume": vol}

# --- PAGE 1: MARKET SUMMARY ---
if st.session_state.page == "📊 Market Summary":
    st.header("📊 Market Wide Summary")
    with st.spinner("Compiling Market Data..."):
        summary_list = [get_stock_stats(s) for s in all_stocks[:12]] # Showing top 12 for speed
        df = pd.DataFrame([s for s in summary_list if s])
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.info("Tip: Go to 'Stock Profile' to search any custom ticker.")

# --- PAGE 2: INDUSTRY MOVERS ---
elif st.session_state.page == "🏢 Industry Movers":
    st.header("🏢 Industry Performance")
    selected_ind = st.selectbox("Select Industry", list(industry_map.keys()))
    
    stocks = industry_map[selected_ind]
    ind_data = []
    for s in stocks:
        stats = get_stock_stats(s)
        if stats: ind_data.append(stats)
    
    df_ind = pd.DataFrame(ind_data)
    st.table(df_ind)
    
    st.subheader("Quick Select Profile")
    cols = st.columns(len(stocks))
    for i, s in enumerate(stocks):
        if cols[i].button(s):
            st.session_state.selected_stock = s
            st.session_state.page = "📈 Stock Profile"
            st.rerun()

# --- PAGE 3: STOCK PROFILE (WITH IMPROVED TREND LINES) ---
elif st.session_state.page == "📈 Stock Profile":
    ticker = st.session_state.selected_stock
    st.header(f"📈 {ticker} - Technical Profile")
    
    # Search Box
    search = st.text_input("Search Ticker (e.g. ZOMATO)", value=ticker).upper()
    if search != ticker:
        st.session_state.selected_stock = search
        st.rerun()

    data = yf.download(f"{search}.NS", period="1y", interval="1d", auto_adjust=True)
    
    if not data.empty:
        # KPI metrics
        ltp = data['Close'].iloc[-1].item()
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.metric("Current Price", f"₹{ltp:,.2f}")
            if st.button("➕ Add to Watchlist"):
                if search not in st.session_state.watchlist:
                    st.session_state.watchlist.append(search)
                    st.success(f"{search} Added!")
        
        with col1:
            # IMPROVED TREND GRAPH
            fig = go.Figure()
            # The "Area Trend" - Most visual for trendlines
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Close'],
                fill='tozeroy', 
                mode='lines',
                line=dict(width=3, color='#00CC96'),
                fillcolor='rgba(0, 204, 150, 0.1)',
                name="Trend"
            ))
            fig.update_layout(
                template="plotly_white",
                height=500,
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            

# --- PAGE 4: WATCHLIST ---
elif st.session_state.page == "⭐ My Watchlist":
    st.header("⭐ My Watchlist")
    if not st.session_state.watchlist:
        st.write("Your watchlist is empty. Go to Stock Profile to add some!")
    else:
        watch_data = []
        for s in st.session_state.watchlist:
            stats = get_stock_stats(s)
            if stats: watch_data.append(stats)
        
        st.dataframe(pd.DataFrame(watch_data), use_container_width=True, hide_index=True)
        if st.button("Clear Watchlist"):
            st.session_state.watchlist = []
            st.rerun()