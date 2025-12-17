import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. LUXURY UI & SUGGESTION BOX STYLING ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, sans-serif; }
    
    /* Interactive Suggestion Box */
    .suggestion-container {
        background: rgba(48, 209, 88, 0.1);
        border: 2px solid #30D158;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 25px;
        animation: fadeIn 0.8s ease-in;
    }
    .sig-label { color: #30D158; font-size: 0.75rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
    .sig-value { font-size: 2.2rem; font-weight: 700; margin: 10px 0; color: #FFFFFF; }
    .sig-desc { color: #8E8E93; font-size: 0.85rem; }

    /* Index Table Styling */
    [data-testid="stMetric"] { background: #1C1C1E; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Navigation logic
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- 2. INDEX CONSTITUENTS ---
INDEX_DATA = {
    "NIFTY 50": [{"Symbol": "HDFCBANK.NS", "Name": "HDFC Bank"}, {"Symbol": "RELIANCE.NS", "Name": "Reliance"}],
    "SENSEX": [{"Symbol": "ICICIBANK.NS", "Name": "ICICI Bank"}, {"Symbol": "INFY.NS", "Name": "Infosys"}],
    "S&P 500": [{"Symbol": "NVDA", "Name": "NVIDIA"}, {"Symbol": "AAPL", "Name": "Apple Inc."}],
    "NASDAQ": [{"Symbol": "MSFT", "Name": "Microsoft"}, {"Symbol": "AMZN", "Name": "Amazon"}]
}

# --- 3. HOME PAGE ---
if st.session_state.page == "home":
    st.title("FinQuest Pro")
    
    cols = st.columns(4)
    for i, (name, sym) in enumerate({"NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC"}.items()):
        with cols[i]:
            if st.button(name, use_container_width=True): nav("detail", sym)
            
            df_idx = pd.DataFrame(INDEX_DATA[name])
            event = st.dataframe(df_idx, hide_index=True, use_container_width=True, 
                                 on_select="rerun", selection_mode="single-row", key=f"tbl_{name}")
            
            if event.selection.rows:
                nav("detail", df_idx.iloc[event.selection.rows[0]]['Symbol'])

# --- 4. DETAIL PAGE (With Suggestion Box) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    stock = yf.Ticker(t)
    st.button("← BACK", on_click=nav, args=("home",))
    
    st.header(f"Analysis: {t}")
    hist = stock.history(period="1y")

    if not hist.empty:
        # LOGIC FOR SUGGESTION
        current_price = hist['Close'].iloc[-1]
        ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        signal = "ACCUMULATE" if current_price > ma50 else "CAUTION"
        color = "#30D158" if signal == "ACCUMULATE" else "#FF453A"

        # --- THE SUGGESTION BOX ---
        st.markdown(f"""
            <div class="suggestion-container" style="border-color: {color}; background: {color}1A;">
                <div class="sig-label" style="color: {color};">Market Sentiment Signal</div>
                <div class="sig-value">{signal}</div>
                <div class="sig-desc">Price is currently {'above' if current_price > ma50 else 'below'} the 50-Day Moving Average (₹{ma50:,.2f})</div>
            </div>
        """, unsafe_allow_html=True)

        # Main Chart
        fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#007AFF'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Financials in Millions
    st.subheader("Financial Performance (In Millions)")
    try:
        fin = stock.financials
        if not fin.empty:
            st.dataframe((fin.iloc[:, :3] / 1_000_000).style.format("{:,.2f}M"), use_container_width=True)
    except: st.info("Financials unavailable.")