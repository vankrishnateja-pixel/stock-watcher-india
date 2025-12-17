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
    
    /* Hero Branding */
    .hero-container { padding: 40px 20px; text-align: center; border-bottom: 1px solid #1C1C1E; margin-bottom: 30px; }
    .hero-name { font-size: 3rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 5px; }
    .hero-sub { color: #8E8E93; font-size: 0.9rem; letter-spacing: 2px; text-transform: uppercase; }
    
    /* Clickable Index Cards */
    .stButton>button {
        width: 100%; border-radius: 12px; background-color: #1C1C1E; 
        border: 1px solid #2C2C2E; color: white; padding: 20px; transition: 0.3s;
    }
    .stButton>button:hover { border-color: #007AFF; transform: translateY(-2px); background-color: #262629; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & MARKET DATA ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"
if "current_index" not in st.session_state: st.session_state.current_index = "NIFTY 50"

def nav(target, ticker=None, index_name=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    if index_name: st.session_state.current_index = index_name
    st.rerun()

# Definitions of top stocks for each index
index_map = {
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "LT.NS", "SBIN.NS"],
    "S&P 500": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B"],
    "NASDAQ": ["AVGO", "COST", "ADBE", "NFLX", "AMD", "PEP", "AZN", "INTC"],
    "SENSEX": ["ASIANPAINT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "M&M.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS"]
}

# --- 3. PAGE: HOME SCREEN (Luxury Intro + Clickable Directory) ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-sub">FinQuest Pro Terminal</div>
            <div class="hero-name">KRISHNA</div>
            <p style='color: #8E8E93;'>Precision data. Elite design. Click an index to explore.</p>
        </div>
    """, unsafe_allow_html=True)

    # Search Bar
    search = st.text_input("DISCOVER ASSET", placeholder="Enter ticker (e.g. TSLA, TCS.NS)...")
    if search: nav("detail", search.upper())

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4-Column Clickable Grid
    cols = st.columns(4)
    indices = list(index_map.keys())
    for i, name in enumerate(indices):
        with cols[i]:
            if st.button(f"🏛️\n\n{name}"):
                nav("index_view", index_name=name)

# --- 4. PAGE: INDEX VIEW (Dynamic Stock Table) ---
elif st.session_state.page == "index_view":
    idx_name = st.session_state.current_index
    st.markdown(f"<h2 style='text-align: center;'>{idx_name} Leaders</h2>", unsafe_allow_html=True)
    if st.button("← BACK TO TERMINAL"): nav("home")
    
    tickers = index_map.get(idx_name, [])
    
    with st.spinner(f"Accessing {idx_name} data..."):
        rows = []
        for t in tickers:
            try:
                d = yf.download(t, period="2d", progress=False)
                if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
                price = d['Close'].iloc[-1]
                change = ((price - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
                rows.append({"Asset": t.split(".")[0], "Price": f"{price:,.2f}", "Day %": f"{change:+.2f}%"})
            except: pass
        
        # Display as a clean, high-end table
        st.table(pd.DataFrame(rows))
        
        st.markdown("### SELECT FOR ANALYSIS")
        grid_cols = st.columns(2)
        for i, t in enumerate(tickers):
            with grid_cols[i % 2]:
                if st.button(f"OPEN {t.split('.')[0]}", key=f"list_{t}"):
                    nav("detail", t)

# --- 5. PAGE: DETAIL (Trend + Financials + AI Suggestions) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← EXIT TO LIST"): nav("index_view")
    
    df = yf.download(t, period="1y", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        ltp = df['Close'].iloc[-1]
        
        st.markdown(f"<h1 style='text-align:center;'>{t}</h1>", unsafe_allow_html=True)
        
        # Suggestion Box
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        status, color = ("BULLISH", "#30d158") if ltp > ma50 else ("CAUTIOUS", "#ff453a")
        st.markdown(f"""
            <div style="border: 1px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: rgba(0,0,0,0.5);">
                <div style="color: {color}; font-weight: 800;">MARKET STATUS: {status}</div>
                <div style="font-size: 2rem; font-weight: 700;">₹{ma50:,.2f}</div>
                <div style="font-size: 0.8rem; color: #8E8E93;">SUGGESTED ENTRY POINT</div>
            </div>
        """, unsafe_allow_html=True)

        # Price Trend Chart
        
        fig_t = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007aff', width=3), fill='tozeroy', fillcolor='rgba(0, 122, 255, 0.1)'))
        fig_t.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=350, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right"))
        st.plotly_chart(fig_t, use_container_width=True)

        # Financials
        try:
            st.subheader("ANNUAL PERFORMANCE")
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_f = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_f.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_f, use_container_width=True)
        except: st.info("Financial data restricted.")