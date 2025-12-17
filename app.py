import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PREMIUM UI CONFIG ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern Intro & Suggestion Boxes */
    .intro-box { border: 1px solid #38383a; border-radius: 20px; padding: 25px; background: #1c1c1e; text-align: center; margin-bottom: 20px; }
    .suggestion-box { background: rgba(48, 209, 88, 0.1); border: 1px solid #30d158; border-radius: 15px; padding: 20px; margin-top: 10px; }
    .suggestion-wait { background: rgba(255, 69, 58, 0.1); border: 1px solid #ff453a; border-radius: 15px; padding: 20px; margin-top: 10px; }
    
    /* Interactive Buttons */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; background-color: #1c1c1e; 
        border: 1px solid #38383a; color: white; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2c2c2e; border-color: #007aff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & DATA ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

def get_clean_data(ticker, period="1y"):
    df = yf.download(ticker, period=period, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# --- 3. PAGE: HOME SCREEN (Krishna's Intro + Financials) ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="intro-box">
            <h1 style='color: #007aff; margin:0;'>Krishna</h1>
            <p style='color: #8e8e93; font-size: 1.1em;'>Creator of FinQuest Pro</p>
            <p>Welcome to your terminal. I've designed this app to give you 
            pro-level stock insights with the simplicity of a mobile app.</p>
        </div>
    """, unsafe_allow_html=True)

    # Home Screen Financial Chart (Global Overview)
    st.subheader("📊 Major Market Indices")
    indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Sensex": "^BSESN", "Nasdaq": "^IXIC"}
    idx_list = []
    for name, sym in indices.items():
        try:
            val = yf.download(sym, period="1d", progress=False)['Close'].iloc[-1]
            idx_list.append({"Market": name, "Value": val})
        except: pass
    
    if idx_list:
        fig_idx = px.bar(pd.DataFrame(idx_list), x='Market', y='Value', color='Market', template="plotly_dark")
        fig_idx.update_layout(plot_bgcolor="black", paper_bgcolor="black", showlegend=False, height=300)
        st.plotly_chart(fig_idx, use_container_width=True)

    st.markdown("---")
    st.write("🔍 **Quick Search**")
    q = st.text_input("", placeholder="Enter Ticker (e.g., NVDA, TCS.NS)...")
    if q: nav("detail", q.upper())
    
    if st.button("🇮🇳 View Nifty 50 Leaders"): nav("nifty")

# --- 4. PAGE: NIFTY 50 TABLE ---
elif st.session_state.page == "nifty":
    st.title("🇮🇳 Nifty 50 Top Stocks")
    if st.button("← Back to Home"): nav("home")
    
    tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", "AXISBANK.NS"]
    
    # Table Display
    rows = []
    for t in tickers:
        try:
            d = yf.download(t, period="2d", progress=False)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            price = d['Close'].iloc[-1]
            change = ((price - d['Close'].iloc[-2]) / d['Close'].iloc[-2]) * 100
            rows.append({"Ticker": t, "Price": f"₹{price:,.2f}", "Day %": f"{change:+.2f}%"})
        except: pass
    
    st.table(pd.DataFrame(rows))
    
    st.write("### Analyze Deeply")
    cols = st.columns(2)
    for i, t in enumerate(tickers):
        with cols[i % 2]:
            if st.button(f"Analyze {t.split('.')[0]}", key=f"btn_{t}"): nav("detail", t)

# --- 5. PAGE: DETAIL (Trend + Financials + Suggestions) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back"): nav("home")
    
    df = get_clean_data(t)
    if not df.empty:
        ltp = df['Close'].iloc[-1]
        st.header(f"{t}")
        
        # 💡 AI Suggestion Box
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        status, sug, box = ("Bullish", "Above 50-DMA.", "suggestion-box") if ltp > ma50 else ("Cautious", "Below 50-DMA.", "suggestion-wait")
        
        st.markdown(f'<div class="{box}"><h3>💡 {status}</h3><p>{sug}</p><h2>🎯 Suggested Entry: ₹{ma50:,.2f}</h2></div>', unsafe_allow_html=True)

        # Restored Trend Line Chart
        fig_t = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007aff', width=3), fill='tozeroy'))
        fig_t.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=350, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_t, use_container_width=True)

        # Financials Bar Chart
        try:
            st.subheader("📊 Annual Financials")
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_f = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_f.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_f, use_container_width=True)
        except: st.info("Financials unavailable for this ticker.")