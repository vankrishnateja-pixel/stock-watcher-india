import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. LUXURY UI CONFIG ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, sans-serif; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Elegant Hero Section */
    .hero-container { padding: 60px 20px; text-align: center; border-bottom: 1px solid #1C1C1E; margin-bottom: 40px; }
    .hero-name { font-size: 1rem; font-weight: 400; letter-spacing: 5px; color: #8E8E93; text-transform: uppercase; margin-bottom: 15px; }
    .hero-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; line-height: 1; margin-bottom: 25px; }
    .hero-description { font-size: 1.1rem; color: #8E8E93; max-width: 700px; margin: 0 auto; line-height: 1.6; }
    
    /* Index Cards as Portals */
    .stButton>button {
        width: 100%; border-radius: 12px; background-color: #1C1C1E; 
        border: 1px solid #2C2C2E; color: white; padding: 25px; transition: 0.3s;
        font-weight: 600; font-size: 1rem;
    }
    .stButton>button:hover { border-color: #007AFF; transform: translateY(-3px); background-color: #262629; color: #007AFF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & MARKET DATA MAP ---
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

# --- 3. PAGE: HOME SCREEN (The "Intel" Intro) ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-name">BY KRISHNA</div>
            <div class="hero-title">The FinQuest Terminal</div>
            <div class="hero-description">
                FinQuest Pro is a high-fidelity market intelligence platform designed to bridge the gap between 
                complex algorithmic data and actionable human insight. Using real-time technical analysis 
                and institutional-grade reporting, we provide clear entry targets and trend signals 
                across global equity markets.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Search Bar Section
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        search = st.text_input("", placeholder="Search Global Symbols (e.g. NVDA, TCS.NS)...")
        if search: nav("detail", search.upper())

    st.markdown("<br><h4 style='text-align: center; color: #48484A; letter-spacing: 2px;'>MARKET DIRECTORY</h4>", unsafe_allow_html=True)
    
    # Clickable Index Grid
    cols = st.columns(4)
    indices = list(index_map.keys())
    for i, name in enumerate(indices):
        with cols[i]:
            if st.button(f"{name}"):
                nav("index_view", index_name=name)

# --- 4. PAGE: INDEX VIEW (Dynamic List) ---
elif st.session_state.page == "index_view":
    idx_name = st.session_state.current_index
    st.markdown(f"<h2 style='text-align: center; letter-spacing: -1px;'>{idx_name} Leaders</h2>", unsafe_allow_html=True)
    if st.button("← EXIT TO TERMINAL"): nav("home")
    
    tickers = index_map.get(idx_name, [])
    
    with st.spinner(f"Accessing {idx_name} Liquidity..."):
        rows = []
        for t in tickers:
            try:
                d = yf.download(t, period="2d", progress=False)
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                price = d['Close'].iloc[-1]
                change = ((price - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
                rows.append({"Asset": t.split(".")[0], "Price": f"{price:,.2f}", "Performance": f"{change:+.2f}%"})
            except: pass
        
        st.table(pd.DataFrame(rows))
        
        st.markdown("### DEEP ANALYSIS")
        grid_cols = st.columns(2)
        for i, t in enumerate(tickers):
            with grid_cols[i % 2]:
                if st.button(f"ANALYZE {t.split('.')[0]}", key=f"list_{t}"):
                    nav("detail", t)

# --- 5. PAGE: DETAIL (Elite Analysis) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← BACK TO LIST"): nav("index_view")
    
    df = yf.download(t, period="1y", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = df['Close'].iloc[-1]
        
        st.markdown(f"<h1 style='text-align:center;'>{t}</h1>", unsafe_allow_html=True)
        
        # Elite Suggestion Card
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        status, color = ("BULLISH MOMENTUM", "#30d158") if ltp > ma50 else ("CAUTIOUS TREND", "#ff453a")
        st.markdown(f"""
            <div style="border: 1px solid {color}; border-radius: 15px; padding: 25px; text-align: center; background: rgba(0,0,0,0.3);">
                <div style="color: {color}; font-weight: 800; letter-spacing: 1px;">{status}</div>
                <div style="font-size: 2.5rem; font-weight: 700; margin: 10px 0;">₹{ma50:,.2f}</div>
                <div style="font-size: 0.9rem; color: #8E8E93; text-transform: uppercase;">Optimal Entry Support</div>
            </div>
        """, unsafe_allow_html=True)

        # Performance Visualization
        fig_t = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007aff', width=3), fill='tozeroy', fillcolor='rgba(0, 122, 255, 0.05)'))
        fig_t.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=400, margin=dict(l=0,r=0,t=20,b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right", showgrid=False))
        st.plotly_chart(fig_t, use_container_width=True)

        try:
            st.subheader("FISCAL METRICS")
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_f = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_f.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300, showlegend=False)
            st.plotly_chart(fig_f, use_container_width=True)
        except: pass