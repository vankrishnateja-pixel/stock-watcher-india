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
    
    /* Clickable Index Cards */
    div[data-testid="stColumn"] > div > div > .stButton > button {
        background-color: #1C1C1E !important;
        border: 2px solid #3A3A3C !important;
        border-radius: 12px;
        padding: 20px 10px !important;
        width: 100%;
        transition: 0.3s;
    }
    div[data-testid="stColumn"] > div > div > .stButton > button:hover {
        border-color: #007AFF !important;
        transform: translateY(-2px);
    }
    .index-name { color: #8E8E93; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;}
    .index-val { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; }

    /* AI Suggestion Box */
    .suggestion-box {
        border: 2px solid #30D158; border-radius: 15px; padding: 25px; 
        text-align: center; background: rgba(48, 209, 88, 0.05); margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation logic
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- 2. HOME PAGE (Clickable Indices) ---
if st.session_state.page == "home":
    st.markdown("<div style='text-align:center; padding:30px 0;'><h1 style='letter-spacing:-1px; margin:0;'>FinQuest Pro</h1><p style='color:#8E8E93; text-transform:uppercase; font-size:0.7rem; letter-spacing:3px;'>By Krishna</p></div>", unsafe_allow_html=True)
    
    # Indices Grid
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
    cols = st.columns(4)
    for i, (name, sym) in enumerate(indices.items()):
        with cols[i]:
            # Fetching price for the button label
            try:
                price = yf.Ticker(sym).fast_info['last_price']
                label = f"{name}\n\n{price:,.0f}"
            except: label = f"{name}\n\n---"
            
            if st.button(label, key=f"btn_{sym}"):
                nav("detail", sym)

    st.write("###")
    search = st.text_input("", placeholder="Search Global Ticker (e.g. NVDA, TCS.NS)...", label_visibility="collapsed")
    if search: nav("detail", search.upper())

# --- 3. DETAIL PAGE (Suggestion -> Chart -> Financials) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    stock = yf.Ticker(t)
    if st.button("← BACK TO TERMINAL"): nav("home")
    
    st.title(t)
    
    # A. Suggestion Box
    df = stock.history(period="1y")
    if not df.empty:
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        st.markdown(f"""<div class='suggestion-box'>
            <div style='color:#30D158; font-weight:800; font-size:0.7rem; letter-spacing:2px;'>MARKET SIGNAL</div>
            <div style='font-size:2.5rem; font-weight:700;'>{ma50:,.2f}</div>
            <div style='color:#8E8E93; font-size:0.8rem;'>Recommended Institutional Support (50-DMA)</div>
        </div>""", unsafe_allow_html=True)

        # B. Trend Chart (2025 Standard)
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007AFF', width=2), fill='tozeroy', fillcolor='rgba(0,122,255,0.05)')])
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_showgrid=False, yaxis_showgrid=False, paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, width="stretch")

    # C. Financials (At the bottom, in Millions)
    st.write("### Financial Performance (Values in Millions)")
    try:
        fin = stock.financials
        if not fin.empty:
            # Convert to millions and format
            fin_millions = fin.iloc[:, :4] / 1_000_000
            st.dataframe(fin_millions.style.format("{:,.2f}M"), width="stretch")
        else: st.info("Financial reporting unavailable for this symbol.")
    except: st.error("Could not retrieve financial data.")