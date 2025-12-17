import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- LUXURY UI CONFIG (Updated for visibility) ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    /* High-Contrast Card Style */
    .news-card {
        background: #1C1C1E;
        border-left: 4px solid #007AFF;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .news-title { font-weight: 700; color: #FFFFFF; text-decoration: none; font-size: 1rem; }
    .news-meta { color: #8E8E93; font-size: 0.8rem; margin-top: 5px; }
    
    .fin-metric { 
        background: #1C1C1E; border: 1px solid #3A3A3C; 
        padding: 10px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation logic (same as previous)
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "AAPL"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- DETAIL PAGE WITH FINANCIALS & NEWS ---
if st.session_state.page == "detail":
    t_symbol = st.session_state.ticker
    stock = yf.Ticker(t_symbol)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.button("← BACK", on_click=nav, args=("home",))
        st.title(f"{t_symbol} Analysis")
        
        # 1. FINANCIALS SECTION
        st.subheader("Key Financials (Annual)")
        try:
            # Fetching Financials
            fin = stock.financials
            if not fin.empty:
                # Selecting key rows if they exist
                keys = ['Total Revenue', 'Net Income', 'EBITDA']
                available_keys = [k for k in keys if k in fin.index]
                display_fin = fin.loc[available_keys].iloc[:, :3] # Last 3 years
                st.dataframe(display_fin.style.format("{:,.0f}").background_gradient(cmap='Blues'))
            else:
                st.info("Detailed financials currently restricted by provider. Check back shortly.")
        except:
            st.error("Could not load financial tables.")

        # 2. TREND CHART
        hist = stock.history(period="1y")
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 3. LIVE NEWS SECTION
        st.subheader("Market News")
        news_list = stock.news
        if news_list:
            for item in news_list[:5]: # Show top 5 news items
                with st.container():
                    st.markdown(f"""
                        <div class="news-card">
                            <a class="news-title" href="{item['link']}" target="_blank">{item['title']}</a>
                            <div class="news-meta">{item['publisher']} • {pd.to_datetime(item['providerPublishTime'], unit='s').strftime('%Y-%m-%d')}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No recent news found for this ticker.")

# --- HOME PAGE ---
else:
    st.title("FinQuest Pro")
    search = st.text_input("Search Ticker", placeholder="AAPL, TSLA, RELIANCE.NS...")
    if search: nav("detail", search.upper())
    
    st.write("### Popular Tickers")
    c1, c2, c3 = st.columns(3)
    if c1.button("Apple (AAPL)"): nav("detail", "AAPL")
    if c2.button("Nvidia (NVDA)"): nav("detail", "NVDA")
    if c3.button("Reliance (RELIANCE.NS)"): nav("detail", "RELIANCE.NS")