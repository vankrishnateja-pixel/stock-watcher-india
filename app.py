import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. MOBILE-FIRST UI CONFIG ---
st.set_page_config(page_title="FinQuest", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "Lively" Mobile Experience
st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto; }
    
    /* Remove huge top padding */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Sleek Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(28, 28, 30, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Typography Fixes */
    h1 { font-size: 1.8rem !important; font-weight: 800 !important; margin-bottom: 0px !important; }
    .stCaption { font-size: 0.9rem !important; color: #8E8E93 !important; }

    /* Thumb-friendly Buttons */
    .stButton>button {
        border-radius: 12px;
        height: 3em;
        background-color: #1c1c1e;
        border: 1px solid #38383a;
        transition: all 0.2s;
    }
    .stButton>button:active { transform: scale(0.95); background-color: #2c2c2e; }
    
    /* Full-width Charts on Mobile */
    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"

ticker = st.session_state.selected_ticker
stock = yf.Ticker(ticker)
data = stock.history(period="5d", interval="1d")

if not data.empty and len(data) >= 2:
    if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
    
    # Header Info
    ltp = data['Close'].iloc[-1]
    pct = ((ltp / data['Close'].iloc[-2]) - 1) * 100
    color = "#30d158" if pct >= 0 else "#ff453a"

    # --- 3. MAIN UI ---
    st.title(stock.info.get('shortName', ticker))
    st.caption(f"{ticker} • {stock.info.get('exchange', 'Market')}")
    
    # Modern Metric Row
    c1, c2 = st.columns(2)
    c1.metric("Price", f"₹{ltp:,.2f}", f"{pct:+.2f}%")
    c2.metric("Day High", f"₹{data['High'].iloc[-1]:,.2f}")

    # Timeframe Selector
    res = st.segmented_control("Range", options=["1D", "1M", "1Y"], default="1Y")
    
    # Fetch Data for Chart
    c_period = res.lower()
    c_interval = "2m" if res == "1D" else "1d"
    chart_df = yf.download(ticker, period=c_period, interval=c_interval, progress=False)
    
    if not chart_df.empty:
        if isinstance(chart_df.columns, pd.MultiIndex): chart_df.columns = chart_df.columns.get_level_values(0)
        
        # Area Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df.index, y=chart_df['Close'], fill='tozeroy',
            line=dict(color=color, width=3),
            fillcolor=f"rgba({(48 if pct >= 0 else 255)}, {(209 if pct >= 0 else 69)}, {(88 if pct >= 0 else 58)}, 0.1)"
        ))
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black",
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False), yaxis=dict(side="right", showgrid=True, gridcolor="#1c1c1e")
        )
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

    # --- 4. CLICKABLE "LIVELY" LISTS ---
    st.markdown("### ⚡ Quick Switch")
    # Using columns to create a "grid" of big touchable buttons
    quick_list = ["AAPL", "NVDA", "TCS.NS", "ZOMATO.NS"]
    cols = st.columns(2)
    for i, t in enumerate(quick_list):
        with cols[i % 2]:
            if st.button(f"🚀 {t}", key=f"btn_{t}"):
                st.session_state.selected_ticker = t
                st.rerun()

else:
    st.error("Market connection busy. Pull down to refresh.")