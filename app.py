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
        transform: translateY(-2px);
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

# --- 2. INDEX CONSTITUENTS DATA ---
# Pre-defined top stocks for each index (2025 weights)
INDEX_DATA = {
    "NIFTY 50": [
        {"Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Weight": "13.71%"},
        {"Symbol": "RELIANCE.NS", "Company": "Reliance Industries", "Weight": "10.12%"},
        {"Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Weight": "9.41%"},
        {"Symbol": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Weight": "6.07%"},
        {"Symbol": "TCS.NS", "Company": "TCS", "Weight": "5.62%"}
    ],
    "SENSEX": [
        {"Symbol": "HDFCBANK.NS", "Company": "HDFC Bank", "Weight": "14.80%"},
        {"Symbol": "RELIANCE.NS", "Company": "Reliance Ind.", "Weight": "10.10%"},
        {"Symbol": "ICICIBANK.NS", "Company": "ICICI Bank", "Weight": "9.50%"},
        {"Symbol": "BHARTIARTL.NS", "Company": "Bharti Airtel", "Weight": "6.20%"},
        {"Symbol": "INFY.NS", "Company": "Infosys", "Weight": "5.40%"}
    ],
    "S&P 500": [
        {"Symbol": "NVDA", "Company": "NVIDIA", "Weight": "7.04%"},
        {"Symbol": "AAPL", "Company": "Apple Inc.", "Weight": "6.61%"},
        {"Symbol": "MSFT", "Company": "Microsoft", "Weight": "5.77%"},
        {"Symbol": "AMZN", "Company": "Amazon", "Weight": "3.88%"},
        {"Symbol": "GOOGL", "Company": "Alphabet (A)", "Weight": "3.12%"}
    ],
    "NASDAQ": [
        {"Symbol": "NVDA", "Company": "NVIDIA", "Weight": "13.03%"},
        {"Symbol": "AAPL", "Company": "Apple Inc.", "Weight": "12.24%"},
        {"Symbol": "MSFT", "Company": "Microsoft", "Weight": "10.68%"},
        {"Symbol": "AMZN", "Company": "Amazon", "Weight": "7.18%"},
        {"Symbol": "GOOGL", "Company": "Alphabet (A)", "Weight": "5.78%"}
    ]
}

# --- 3. HOME PAGE ---
if st.session_state.page == "home":
    st.markdown("<div style='text-align:center; padding:30px 0;'><h1 style='margin:0;'>FinQuest Pro</h1><p style='color:#8E8E93;'>By Krishna</p></div>", unsafe_allow_html=True)
    
    indices = {"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
    cols = st.columns(4)
    
    for i, (name, sym) in enumerate(indices.items()):
        with cols[i]:
            try:
                price = yf.Ticker(sym).fast_info['last_price']
                label = f"{name}\n{price:,.0f}"
            except: label = f"{name}\n---"
            
            if st.button(label, key=f"btn_{sym}"):
                nav("detail", sym)
            
            # Index Table
            df_index = pd.DataFrame(INDEX_DATA[name])
            st.dataframe(df_index, hide_index=True, use_container_width=True)

    st.write("###")
    search = st.text_input("", placeholder="Search Ticker (e.g. TSLA, TCS.NS)...", label_visibility="collapsed")
    if search: nav("detail", search.upper())

# --- 4. DETAIL PAGE ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    stock = yf.Ticker(t)
    if st.button("← BACK"): nav("home")
    
    st.title(t)
    
    df = stock.history(period="1y")
    if not df.empty:
        # A. Signal
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        st.markdown(f"""<div class='suggestion-box'>
            <div style='color:#30D158; font-weight:800; font-size:0.7rem; letter-spacing:2px;'>MARKET SIGNAL</div>
            <div style='font-size:2.5rem; font-weight:700;'>{ma50:,.2f}</div>
            <div style='color:#8E8E93; font-size:0.8rem;'>50-Day Moving Average Support</div>
        </div>""", unsafe_allow_html=True)

        # B. Chart
        fig = go.Figure(data=[go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007AFF', width=2), fill='tozeroy', fillcolor='rgba(0,122,255,0.05)')])
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_showgrid=False, yaxis_showgrid=False, paper_bgcolor='black', plot_bgcolor='black')
        st.plotly_chart(fig, use_container_width=True)

    # C. Financials in Millions
    st.write("### Financial Performance (Millions)")
    try:
        fin = stock.financials
        if not fin.empty:
            fin_millions = fin.iloc[:, :4] / 1_000_000
            st.dataframe(fin_millions.style.format("{:,.2f}M"), use_container_width=True)
    except: st.info("Financial data feed unavailable.")