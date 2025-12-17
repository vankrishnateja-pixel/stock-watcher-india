import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. LUXURY UI CONFIG ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, sans-serif; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Home Screen Index Grid */
    .index-card {
        background: #1C1C1E; border: 1px solid #3A3A3C; border-radius: 12px;
        padding: 15px; text-align: center; margin-bottom: 10px;
    }
    .index-name { color: #8E8E93; font-size: 0.8rem; letter-spacing: 1px; }
    .index-val { font-size: 1.2rem; font-weight: 700; color: #007AFF; }

    /* News & Suggestions */
    .suggestion-box {
        border: 2px solid #30D158; border-radius: 15px; padding: 20px; 
        text-align: center; background: rgba(48, 209, 88, 0.1); margin-bottom: 25px;
    }
    .news-card {
        background: #1C1C1E; border-left: 4px solid #007AFF;
        border-radius: 8px; padding: 12px; margin-bottom: 10px;
    }
    .news-link { color: #FFFFFF; text-decoration: none; font-weight: 600; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# Navigation logic
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- 2. HOME PAGE (Indices + Search) ---
if st.session_state.page == "home":
    st.markdown("<div style='text-align:center; padding:20px;'><h1 style='margin:0;'>FinQuest Pro</h1><p style='color:#8E8E93;'>By Krishna</p></div>", unsafe_allow_html=True)
    
    # Indices Grid
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
    cols = st.columns(4)
    for i, (name, sym) in enumerate(indices.items()):
        with cols[i]:
            try:
                val = yf.download(sym, period="1d", progress=False)['Close'].iloc[-1]
                st.markdown(f"<div class='index-card'><div class='index-name'>{name}</div><div class='index-val'>{val:,.0f}</div></div>", unsafe_allow_html=True)
            except: st.markdown(f"<div class='index-card'><div class='index-name'>{name}</div><div class='index-val'>---</div></div>", unsafe_allow_html=True)

    st.write("###")
    search = st.text_input("", placeholder="Search Ticker (e.g. NVDA, TCS.NS)...", label_visibility="collapsed")
    if search: nav("detail", search.upper())

# --- 3. DETAIL PAGE (Suggestions -> Chart -> News -> Financials) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    stock = yf.Ticker(t)
    if st.button("← BACK"): nav("home")
    
    st.title(t)
    
    # A. Suggestion Box (Top)
    df = stock.history(period="1y")
    if not df.empty:
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        st.markdown(f"""<div class='suggestion-box'>
            <div style='color:#30D158; font-weight:800; font-size:0.7rem; letter-spacing:2px;'>AI SIGNAL</div>
            <div style='font-size:2rem; font-weight:700;'>₹{ma50:,.2f}</div>
            <div style='color:#8E8E93; font-size:0.8rem;'>Recommended Entry Point (50-DMA)</div>
        </div>""", unsafe_allow_html=True)

        # B. Trend Chart
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007AFF', width=2))])
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), xaxis_showgrid=False, yaxis_showgrid=False)
        st.plotly_chart(fig, width="stretch")

    # C. External News Links
    st.write("### Latest Intelligence")
    news = stock.news
    if news:
        for item in news[:4]:
            url = item.get('link', item.get('url', '#'))
            st.markdown(f"""<div class='news-card'>
                <a class='news-link' href='{url}' target='_blank'>{item.get('title', 'Market Update')}</a>
                <div style='color:#8E8E93; font-size:0.75rem; margin-top:4px;'>{item.get('publisher', 'Source')}</div>
            </div>""", unsafe_allow_html=True)

    # D. Financials (At the Bottom)
    st.write("### Financial Performance")
    try:
        fin = stock.financials
        if not fin.empty:
            st.dataframe(fin.iloc[:, :3], width="stretch")
        else: st.info("Annual reporting data currently unavailable for this ticker.")
    except: st.error("Financial feed error.")