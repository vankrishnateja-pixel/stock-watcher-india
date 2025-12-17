import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. LUXURY UI CONFIG ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .news-card {
        background: #1C1C1E; border-left: 4px solid #007AFF;
        border-radius: 8px; padding: 15px; margin: 10px 0;
    }
    .news-title { font-weight: 700; color: #FFFFFF; text-decoration: none; display: block; }
    .news-meta { color: #8E8E93; font-size: 0.8rem; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# --- 2. DETAIL PAGE (Debugged News & Charts) ---
if st.session_state.page == "detail":
    t_symbol = st.session_state.ticker
    stock = yf.Ticker(t_symbol)
    
    if st.button("← BACK"): nav("home")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title(f"{t_symbol}")
        
        # Financials - Safely handled
        try:
            fin = stock.financials
            if not fin.empty:
                st.subheader("Key Financials")
                st.dataframe(fin.iloc[:, :3], width="stretch") # Using new 'stretch' width
            else:
                st.info("Financial tables restricted by provider.")
        except:
            st.error("Financial data unavailable.")

        # Chart - Updated to avoid deprecation warning
        hist = stock.history(period="1y")
        if not hist.empty:
            fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#007AFF'))])
            fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, width="stretch") # Fixed use_container_width warning

    with col2:
        st.subheader("Market News")
        try:
            news_list = stock.news
            if news_list:
                for item in news_list[:5]:
                    # FIX: Safely get link or fallback to empty string
                    link = item.get('link', item.get('url', '#')) 
                    title = item.get('title', 'No Title Available')
                    publisher = item.get('publisher', 'Unknown Source')
                    
                    st.markdown(f"""
                        <div class="news-card">
                            <a class="news-title" href="{link}" target="_blank">{title}</a>
                            <div class="news-meta">{publisher}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No news available for this asset.")
        except Exception as e:
            st.write("News feed temporarily offline.")

# --- 3. HOME PAGE ---
else:
    st.title("FinQuest Pro")
    search = st.text_input("Enter Ticker", placeholder="e.g., NVDA, AAPL, TCS.NS")
    if search: nav("detail", search.upper())