import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIG & UI STYLE ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Suggestion Box Styling */
    .suggestion-box {
        background: rgba(48, 209, 88, 0.1); 
        border: 1px solid #30d158;
        border-radius: 15px; 
        padding: 20px; 
        margin-top: 20px;
    }
    .suggestion-wait {
        background: rgba(255, 69, 58, 0.1); 
        border: 1px solid #ff453a;
        border-radius: 15px; 
        padding: 20px; 
        margin-top: 20px;
    }
    
    .stTextInput>div>div>input {
        background-color: #1c1c1e; color: white; border: 1px solid #38383a;
        border-radius: 12px; padding: 10px;
    }
    .stButton>button {
        width: 100%; border-radius: 15px; height: 3.5em; font-size: 1.1em;
        background-color: #1C1C1E; border: 1px solid #38383a; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & DATA ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

def get_clean_data(ticker, period="2y"):
    df = yf.download(ticker, period=period, progress=False)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# --- 3. GLOBAL SEARCH ---
query = st.text_input("🔍 Search Ticker", placeholder="Enter symbol (e.g. AAPL, TCS.NS)...", key="global_search")
if query:
    if st.button(f"Go to {query.upper()}"):
        nav("detail", query.upper())

# --- 4. PAGE: LANDING ---
if st.session_state.page == "home":
    st.title("FinQuest Pro")
    st.write("I am **Krishna**, the creator of FinQuest Pro. Navigate markets with precision.")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Global Stocks"): nav("global")
        if st.button("🇺🇸 S&P 500"): nav("sp500")
    with col2:
        if st.button("🇮🇳 Nifty 50"): nav("nifty")
        if st.button("📉 Sensex India"): nav("sensex")

# --- 5. PAGE: STOCK DETAIL (WITH SUGGESTIONS) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back"): nav("home")
    
    df = get_clean_data(t)
    if not df.empty:
        # Current Price Info
        ltp = df['Close'].iloc[-1]
        change = ltp - df['Close'].iloc[-2]
        
        st.title(f"{t}")
        st.metric("Price", f"₹{ltp:,.2f}", f"{change:+.2f}")

        # --- AI SUGGESTION BOX ---
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # Logic for suggestions
        if ltp > ma50 > ma200:
            status = "Strong Bullish"
            suggestion = "The stock is in a strong uptrend. High momentum."
            suggested_price = ma50 * 1.02 # Buy slightly above support
            box_class = "suggestion-box"
        elif ltp < ma50:
            status = "Cooling Down"
            suggestion = "Trading below 50-day average. Wait for a reversal."
            suggested_price = ma50 * 0.95 # Buy at a discount
            box_class = "suggestion-wait"
        else:
            status = "Neutral"
            suggestion = "Consolidating. Look for a breakout above recent highs."
            suggested_price = ltp
            box_class = "suggestion-box"

        st.markdown(f"""
            <div class "{box_class}">
                <h3 style="margin-top:0;">💡 Analyst Suggestion: {status}</h3>
                <p>{suggestion}</p>
                <h2 style="margin-bottom:0; color:white;">🎯 Target Entry: ₹{suggested_price:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

        # Trend Chart
        st.markdown("---")
        line_color = "#30d158" if change >= 0 else "#ff453a"
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df.index, y=df['Close'], line=dict(color=line_color, width=3), fill='tozeroy'))
        fig_trend.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_trend, width='stretch')

        # Financials
        try:
            st.subheader("📊 Annual Revenue vs Net Income")
            stock = yf.Ticker(t)
            fin = stock.financials.T[['Total Revenue', 'Net Income']].head(4)
            fig_fin = px.bar(fin, barmode='group', template="plotly_dark", color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
            fig_fin.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
            st.plotly_chart(fig_fin, width='stretch')
        except:
            st.info("Financial statements unavailable.")