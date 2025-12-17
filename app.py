import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. APPLE STOCKS DESIGN ---
st.set_page_config(page_title="Stocks", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    section[data-testid="stSidebar"] {
        background-color: #1c1c1e !important;
        border-right: 1px solid #38383a;
        width: 350px !important;
    }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 700 !important; color: white !important; }
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
    .stButton>button:hover { background-color: #2c2c2e; }
    /* Style for the search result selection */
    div[data-baseweb="select"] { background-color: #2c2c2e; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SEARCH LOGIC ---
def search_stocks(query):
    """Uses yfinance to find tickers based on company names."""
    try:
        search = yf.Search(query, max_results=8)
        # Filter for stocks/equities and format for the dropdown
        results = []
        for quote in search.quotes:
            display_name = f"{quote['symbol']} - {quote.get('shortname', 'Unknown')}"
            results.append({"symbol": quote['symbol'], "display": display_name})
        return results
    except Exception:
        return []

# --- 3. STATE MANAGEMENT ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"

# --- 4. SIDEBAR WATCHLIST & SEARCH ---
with st.sidebar:
    st.title("Stocks")
    
    # Company Name Search Box
    search_query = st.text_input("Search Company Name", placeholder="e.g. Apple or Tata Motors")
    
    if search_query:
        matches = search_stocks(search_query)
        if matches:
            options = {m['display']: m['symbol'] for m in matches}
            selected_from_search = st.selectbox("Select Result:", options.keys(), index=None, placeholder="Choose a company...")
            if selected_from_search:
                st.session_state.selected_ticker = options[selected_from_search]
        else:
            st.caption("No matches found.")

    st.markdown("---")
    st.subheader("Watchlist")
    watchlist = ["RELIANCE.NS", "AAPL", "TSLA", "TCS.NS", "NVDA", "ZOMATO.NS"]
    for stock in watchlist:
        if st.button(f"**{stock}**"):
            st.session_state.selected_ticker = stock

# --- 5. DATA FETCHING & DISPLAY ---
ticker = st.session_state.selected_ticker
stock_obj = yf.Ticker(ticker)
data = stock_obj.history(period="1d", interval="2m")

if not data.empty:
    # Get Metadata
    info = stock_obj.info
    long_name = info.get('longName', ticker)
    
    # Calculate Changes
    ltp = data['Close'].iloc[-1]
    open_price = data['Open'].iloc[0]
    change = ltp - open_price
    pct_change = (change / open_price) * 100
    
    # Header
    st.title(long_name)
    st.caption(f"{ticker} • {info.get('exchange', 'Market')}")
    
    col1, _ = st.columns([1, 3])
    with col1:
        st.metric(label="", value=f"{info.get('currency', '₹')}{ltp:,.2f}", 
                  delta=f"{change:+.2f} ({pct_change:+.2f}%)")

    # Clean Apple Chart
    line_color = "#30d158" if change >= 0 else "#ff453a"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=f'rgba({48 if change >= 0 else 255}, {209 if change >= 0 else 69}, {88 if change >= 0 else 58}, 0.1)',
        hovertemplate="Price: %{y:.2f}<extra></extra>"
    ))

    fig.update_layout(
        plot_bgcolor="black", paper_bgcolor="black",
        xaxis=dict(showgrid=False, color="#8e8e93"),
        yaxis=dict(side="right", gridcolor="#2c2c2e", color="#8e8e93"),
        height=350, margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Market Details
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.write(f"**High**\n\n{data['High'].max():,.2f}")
    m2.write(f"**Low**\n\n{data['Low'].min():,.2f}")
    m3.write(f"**Mkt Cap**\n\n{info.get('marketCap', 0)/1e9:.1f}B")
    m4.write(f"**P/E Ratio**\n\n{info.get('trailingPE', 'N/A')}")
else:
    st.warning(f"Unable to load data for {ticker}. Check the symbol format (e.g., .NS for Indian stocks).")