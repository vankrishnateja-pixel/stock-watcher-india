import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. LUXURY UI CONFIG ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Absolute Dark Mode */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* High-End Hero Section */
    .hero-container {
        padding: 40px 20px;
        text-align: center;
        border-bottom: 1px solid #1C1C1E;
        margin-bottom: 30px;
    }
    .hero-name { font-size: 3rem; font-weight: 800; letter-spacing: -1px; color: #FFFFFF; margin-bottom: 5px; }
    .hero-sub { color: #8E8E93; font-size: 1.1rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; }
    
    /* Premium Index Cards */
    .index-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }
    .index-item {
        background: #1C1C1E; border: 1px solid #2C2C2E; border-radius: 12px;
        padding: 20px; text-align: center; transition: all 0.3s ease;
    }
    .index-item:hover { border-color: #007AFF; transform: translateY(-3px); }
    .index-label { color: #8E8E93; font-size: 0.8rem; font-weight: 600; margin-bottom: 5px; }
    .index-value { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; }

    /* Buttons */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em; background-color: #1C1C1E; 
        border: 1px solid #2C2C2E; color: white; font-weight: 600;
    }
    .stButton>button:hover { border-color: #007AFF; color: #007AFF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & LOGIC ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- 3. PAGE: HOME SCREEN (Krishna's Luxury Intro + Index Directory) ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-sub">FinQuest Pro Terminal</div>
            <div class="hero-name">KRISHNA</div>
            <p style='color: #8E8E93; max-width: 500px; margin: 0 auto; font-style: italic;'>
                "Precision data. Elite design. Your window into the global markets."
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Clean Index List (No Charts)
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "GOLD": "GC=F"
    }
    
    st.markdown('<div style="text-align: center; margin-bottom: 20px; color: #8E8E93; font-weight: 600;">MARKET DIRECTORY</div>', unsafe_allow_html=True)
    
    # We use columns to create the high-end grid
    cols = st.columns(len(indices))
    for i, (name, sym) in enumerate(indices.items()):
        with cols[i]:
            try:
                # Get only the latest price
                price = yf.download(sym, period="1d", progress=False)['Close'].iloc[-1]
                st.markdown(f"""
                    <div class="index-item">
                        <div class="index-label">{name}</div>
                        <div class="index-value">{price:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown(f'<div class="index-item"><div class="index-label">{name}</div><div>Offline</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Elegant Search & Navigation
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        search = st.text_input("DISCOVER ASSET", placeholder="e.g. RELIANCE.NS, TSLA, AAPL")
        if search: nav("detail", search.upper())
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("OPEN NIFTY 50 LEADERS"): nav("nifty")

# --- 4. PAGE: NIFTY 50 TABLE (High-End Table) ---
elif st.session_state.page == "nifty":
    st.markdown("<h2 style='text-align: center;'>NIFTY 50 CONSTITUENTS</h2>", unsafe_allow_html=True)
    if st.button("← EXIT TO TERMINAL"): nav("home")
    
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS"]
    
    # Professional Table Layout
    rows = []
    for t in tickers:
        try:
            d = yf.download(t, period="2d", progress=False)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            price = d['Close'].iloc[-1]
            change = ((price - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            rows.append({"Asset": t.split(".")[0], "Price": f"₹{price:,.2f}", "Performance": f"{change:+.2f}%"})
        except: pass
    
    st.table(pd.DataFrame(rows))
    
    st.markdown("### SELECT FOR ANALYSIS")
    grid_cols = st.columns(2)
    for i, t in enumerate(tickers):
        with grid_cols[i % 2]:
            if st.button(f"SELECT {t.split('.')[0]}", key=f"btn_{t}"): nav("detail", t)

# --- 5. PAGE: DETAIL (Trend + Financials + Suggestions) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← BACK"): nav("home")
    
    # Download data
    df = yf.download(t, period="1y", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        ltp = df['Close'].iloc[-1]
        st.markdown(f"<h1 style='text-align:center;'>{t}</h1>", unsafe_allow_html=True)
        
        # 💡 AI Suggestion Box (Restored)
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        status, color = ("BULLISH", "#30d158") if ltp > ma50 else ("CAUTIOUS", "#ff453a")
        
        st.markdown(f"""
            <div style="border: 1px solid {color}; border-radius: 15px; padding: 20px; text-align: center; background: rgba(0,0,0,0.5);">
                <div style="color: {color}; font-weight: 800; font-size: 1.2rem;">MARKET STATUS: {status}</div>
                <div style="font-size: 0.9rem; color: #8E8E93;">SUGGESTED ENTRY AT SUPPORT</div>
                <div style="font-size: 2rem; font-weight: 700;">₹{ma50:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        # Restored Trend Line Chart
        fig_t = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007aff', width=3), fill='tozeroy', fillcolor='rgba(0, 122, 255, 0.1)'))
        fig_t.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=350, margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right"))
        st.plotly_chart(fig_t, use_container_width=True)

        # Financials Bar Chart
        try:
            st.subheader("ANNUAL REVENUE")
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_f = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_f.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_f, use_container_width=True)
        except: st.info("Financial data restricted.")