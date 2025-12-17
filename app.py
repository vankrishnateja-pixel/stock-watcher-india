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
    
    /* Clickable Index Buttons */
    div[data-testid="stColumn"] > div > div > .stButton > button {
        background-color: #1C1C1E !important;
        border: 2px solid #3A3A3C !important;
        border-radius: 12px;
        padding: 20px 10px !important;
        width: 100%;
        transition: 0.3s;
        white-space: pre-wrap;
    }
    div[data-testid="stColumn"] > div > div > .stButton > button:hover {
        border-color: #007AFF !important;
    }
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

# --- 2. INDEX DATA ---
INDEX_DATA = {
    "NIFTY 50": [
        {"Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Weight": "13.7%"},
        {"Symbol": "RELIANCE.NS", "Company": "Reliance Industries", "Weight": "10.1%"},
        {"Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Weight": "9.4%"},
        {"Symbol": "TCS.NS", "Company": "TCS", "Weight": "5.6%"}
    ],
    "SENSEX": [
        {"Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Weight": "14.8%"},
        {"Symbol": "RELIANCE.NS", "Company": "Reliance Ind.", "Weight": "10.1%"},
        {"Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Weight": "9.5%"},
        {"Symbol": "INFY.NS", "Company": "Infosys", "Weight": "5.4%"}
    ],
    "S&P 500": [
        {"Symbol": "NVDA", "Company": "NVIDIA", "Weight": "7.0%"},
        {"Symbol": "AAPL", "Company": "Apple Inc.", "Weight": "6.6%"},
        {"Symbol": "MSFT", "Company": "Microsoft", "Weight": "5.7%"},
        {"Symbol": "AMZN", "Company": "Amazon", "Weight": "3.8%"}
    ],
    "NASDAQ": [
        {"Symbol": "NVDA", "Company": "NVIDIA", "Weight": "13.0%"},
        {"Symbol": "AAPL", "Company": "Apple Inc.", "Weight": "12.2%"},
        {"Symbol": "MSFT", "Company": "Microsoft", "Weight": "10.6%"},
        {"Symbol": "AMZN", "Company": "Amazon", "Weight": "7.1%"}
    ]
}

# --- 3. HOME PAGE ---
if st.session_state.page == "home":
    st.markdown("<div style='text-align:center; padding:30px 0;'><h1 style='margin:0;'>FinQuest Pro</h1><p style='color:#8E8E93;'>Terminal v2025</p></div>", unsafe_allow_html=True)
    
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
    cols = st.columns(4)
    
    for i, (name, sym) in enumerate(indices.items()):
        with cols[i]:
            if st.button(f"{name}", key=f"btn_{sym}"):
                nav("detail", sym)
            
            df_index = pd.DataFrame(INDEX_DATA[name])
            
            # FIX: Removed width="stretch" and used use_container_width=True
            event = st.dataframe(
                df_index, 
                hide_index=True, 
                use_container_width=True,
                on_select="rerun", 
                selection_mode="single-row",
                key=f"table_{name}"
            )
            
            if event.selection.rows:
                selected_row_idx = event.selection.rows[0]
                selected_ticker = df_index.iloc[selected_row_idx]['Symbol']
                nav("detail", selected_ticker)

    st.write("###")
    search = st.text_input("", placeholder="Quick Search...", label_visibility="collapsed")
    if search: nav("detail", search.upper())

# --- 4. DETAIL PAGE ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    stock = yf.Ticker(t)
    if st.button("← BACK"): nav("home")
    
    st.title(t)
    df = stock.history(period="1y")
    
    if not df.empty:
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        st.markdown(f"<div class='suggestion-box'><div style='color:#30D158; font-weight:800; font-size:0.7rem; letter-spacing:2px;'>SIGNAL</div><div style='font-size:2.5rem; font-weight:700;'>{ma50:,.2f}</div></div>", unsafe_allow_html=True)

        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007AFF', width=2))])
        fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

    st.write("### Financials (Millions)")
    try:
        fin = stock.financials
        if not fin.empty:
            fin_millions = fin.iloc[:, :3] / 1_000_000
            st.dataframe(fin_millions.style.format("{:,.2f}M"), use_container_width=True)
    except: st.info("Financial data not found.")