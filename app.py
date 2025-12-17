import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. LUXURY UI CONFIG (Optimized for Mobile Viewport) ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, sans-serif; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Compact Hero Section */
    .hero-container { padding: 20px 10px; text-align: center; border-bottom: 1px solid #1C1C1E; }
    .hero-name { font-size: 0.8rem; font-weight: 400; letter-spacing: 3px; color: #007AFF; text-transform: uppercase; }
    .hero-title { font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; margin: 5px 0; }
    .hero-description { font-size: 0.9rem; color: #8E8E93; max-width: 90% ; margin: 0 auto; line-height: 1.4; }
    
    /* High-Contrast Index Portals */
    div[data-testid="stColumn"] > div > div > .stButton > button {
        background-color: #1C1C1E !important;
        border: 2px solid #3A3A3C !important; /* Visible Border */
        border-radius: 12px;
        padding: 15px 5px !important;
        height: auto !important;
        min-height: 80px;
    }

    /* Custom Data Cards (Replaces merging tables) */
    .data-card {
        background: #1C1C1E;
        border: 1px solid #3A3A3C;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ticker-name { font-weight: 700; font-size: 1.1rem; }
    .price-val { font-family: monospace; font-size: 1rem; }
    .perf-up { color: #30D158; font-weight: 600; }
    .perf-down { color: #FF453A; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION LOGIC ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"
if "current_index" not in st.session_state: st.session_state.current_index = "NIFTY 50"

def nav(target, ticker=None, index_name=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    if index_name: st.session_state.current_index = index_name
    st.rerun()

index_map = {
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "LT.NS", "SBIN.NS"],
    "S&P 500": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B"],
    "NASDAQ": ["AVGO", "COST", "ADBE", "NFLX", "AMD", "PEP", "AZN", "INTC"],
    "SENSEX": ["ASIANPAINT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "M&M.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS"]
}

# --- 3. PAGE: HOME SCREEN ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-name">BY KRISHNA</div>
            <div class="hero-title">FinQuest Pro</div>
            <div class="hero-description">Institutional-grade intelligence and entry targets for global equity markets.</div>
        </div>
    """, unsafe_allow_html=True)

    # Search Bar (Compact)
    search = st.text_input("", placeholder="Search Ticker (e.g. NVDA)...", label_visibility="collapsed")
    if search: nav("detail", search.upper())

    # The Grid (Now higher up)
    st.write("###")
    cols = st.columns(2) # 2x2 grid is better for mobile fold
    indices = list(index_map.keys())
    for i, name in enumerate(indices):
        with cols[i % 2]:
            if st.button(f"{name}", key=f"idx_{name}"):
                nav("index_view", index_name=name)

# --- 4. PAGE: INDEX VIEW (High-Contrast Cards) ---
elif st.session_state.page == "index_view":
    idx_name = st.session_state.current_index
    st.markdown(f"<h3 style='margin-bottom:0;'>{idx_name} Leaders</h3>", unsafe_allow_html=True)
    if st.button("← BACK"): nav("home")
    
    tickers = index_map.get(idx_name, [])
    
    for t in tickers:
        try:
            d = yf.download(t, period="2d", progress=False)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            price = d['Close'].iloc[-1]
            change = ((price - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            color_class = "perf-up" if change >= 0 else "perf-down"
            
            # Custom HTML Card instead of Table
            st.markdown(f"""
                <div class="data-card">
                    <div>
                        <div class="ticker-name">{t.split('.')[0]}</div>
                        <div class="price-val">₹{price:,.2f}</div>
                    </div>
                    <div class="{color_class}">{change:+.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Analyze {t.split('.')[0]}", key=f"list_{t}"):
                nav("detail", t)
        except: pass

# --- 5. PAGE: DETAIL ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← EXIT"): nav("home")
    
    df = yf.download(t, period="1y", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = df['Close'].iloc[-1]
        
        # Elite Suggestion Card
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        color = "#30D158" if ltp > ma50 else "#FF453A"
        st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: #1C1C1E;">
                <div style="color: {color}; font-weight: 800; font-size: 0.8rem; letter-spacing: 2px;">SUGGESTED ENTRY</div>
                <div style="font-size: 2.2rem; font-weight: 700; margin: 5px 0;">₹{ma50:,.2f}</div>
                <div style="font-size: 0.8rem; color: #8E8E93;">Based on 50-Day Moving Average</div>
            </div>
        """, unsafe_allow_html=True)

        # Trend Chart
        fig_t = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007AFF', width=2), fill='tozeroy', fillcolor='rgba(0, 122, 255, 0.05)'))
        fig_t.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=300, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right", showgrid=False))
        st.plotly_chart(fig_t, use_container_width=True)