import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PREMIUM APPLE STOCKS UI CONFIG ---
st.set_page_config(
    page_title="Stocks", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-contrast iOS look
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    section[data-testid="stSidebar"] { background-color: #1c1c1e !important; border-right: 1px solid #38383a; width: 350px !important; }
    .stMetric { background-color: #1c1c1e; border-radius: 12px; padding: 20px; border: 1px solid #38383a; }
    [data-testid="stMetricValue"] { color: white !important; font-size: 32px !important; font-weight: 700 !important; }
    .stButton>button { 
        width: 100%; background-color: transparent; color: white; border: none; 
        border-bottom: 1px solid #38383a; text-align: left; padding: 12px 10px; border-radius: 0;
    }
    .stButton>button:hover { background-color: #2c2c2e; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE & STATE ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"

def fetch_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex): 
            data.columns = data.columns.get_level_values(0)
        return data
    except: return None

# Index Constituents
index_groups = {
    "🇮🇳 NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS", "TATAMOTORS.NS"],
    "🇺🇸 S&P 500": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B"],
    "🌐 GLOBAL": ["BTC-USD", "ETH-USD", "GC=F"]
}

# --- 3. SIDEBAR: WATCHLIST & CLICKABLE INDICES ---
with st.sidebar:
    st.title("Stocks")
    
    # Search Box
    search_q = st.text_input("Search", placeholder="Company or Ticker...")
    if search_q:
        search_res = yf.Search(search_q, max_results=3).quotes
        for res in search_res:
            label = f"{res['symbol']} - {res.get('shortname', '')}"
            if st.button(label):
                st.session_state.selected_ticker = res['symbol']
                st.rerun()

    st.markdown("---")
    for group_name, tickers in index_groups.items():
        with st.expander(f"**{group_name}**", expanded=(group_name == "🇮🇳 NIFTY 50")):
            for t in tickers:
                if st.button(f"{t}", key=f"side_{t}"):
                    st.session_state.selected_ticker = t
                    st.rerun()

# --- 4. MAIN DASHBOARD ---
ticker = st.session_state.selected_ticker
stock_obj = yf.Ticker(ticker)

# Fetch current stats
main_data = fetch_data(ticker, period="5d", interval="1d")

if main_data is not None and len(main_data) >= 2:
    info = stock_obj.info
    ltp = main_data['Close'].iloc[-1]
    prev = main_data['Close'].iloc[-2]
    change = ltp - prev
    pct = (change / prev) * 100
    
    st.title(info.get('longName', ticker))
    st.caption(f"{ticker} • {info.get('exchange', 'Market')}")

    col_price, col_sentiment = st.columns([2, 1])
    with col_price:
        st.metric("Price", f"{info.get('currency', '₹')}{ltp:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")

    # FIX: Added a default to prevent NoneType Error
    time_frame = st.segmented_control("Range", options=["1D", "1M", "1Y", "5Y"], default="1Y")
    if not time_frame:
        time_frame = "1Y"
    
    c_period = time_frame.lower()
    c_interval = "2m" if time_frame == "1D" else "1d"
    chart_data = fetch_data(ticker, period=c_period, interval=c_interval)

    if chart_data is not None:
        line_color = "#30d158" if pct >= 0 else "#ff453a"
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['Close'], mode='lines',
            line=dict(color=line_color, width=3),
            fill='tozeroy',
            fillcolor=f"rgba({(48 if pct >= 0 else 255)}, {(209 if pct >= 0 else 69)}, {(88 if pct >= 0 else 58)}, 0.1)",
            hovertemplate="Price: %{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black",
            height=400, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, color="#8e8e93"),
            yaxis=dict(side="right", gridcolor="#2c2c2e", color="#8e8e93"),
            hovermode="x unified"
        )
        # FIX: Updated width for 2025 compliance
        st.plotly_chart(fig, width='stretch')

    # --- 5. FINANCIALS (SAFE VERSION) ---
    st.markdown("### 📊 Financials")
    
    try:
        # We fetch financials separately with error handling
        fin = stock_obj.financials
        if not fin.empty:
            # Transpose and pick top 2 metrics
            plot_df = fin.T[['Total Revenue', 'Net Income']].head(4)
            fig_fin = px.bar(plot_df, barmode='group', template="plotly_dark",
                             color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_fin.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_fin, width='stretch')
        else:
            st.info("Annual financials are currently restricted or unavailable for this ticker.")
    except Exception:
        st.info("Detailed financial charts are not available for this specific asset.")

else:
    st.error(f"⚠️ Market data for {ticker} is currently unavailable. Try a different ticker.")