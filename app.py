import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & UI STYLE ---
st.set_page_config(page_title="FinQuest Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    /* Suggestion Box Styling */
    .suggestion-box { background: rgba(48, 209, 88, 0.1); border: 1px solid #30d158; border-radius: 15px; padding: 20px; margin-top: 10px; }
    .suggestion-wait { background: rgba(255, 69, 58, 0.1); border: 1px solid #ff453a; border-radius: 15px; padding: 20px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "home"
if "ticker" not in st.session_state: st.session_state.ticker = "RELIANCE.NS"

def nav(target, ticker=None):
    st.session_state.page = target
    if ticker: st.session_state.ticker = ticker
    st.rerun()

# List of Top 10 Nifty 50 Tickers
NIFTY_TOP_10 = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
                "HINDUNILVR.NS", "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS"]

# --- 3. PAGE: LANDING ---
if st.session_state.page == "home":
    st.title("FinQuest Pro")
    st.write("Welcome! Choose a market to explore.")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇮🇳 Nifty 50 (Top Stocks)"): nav("nifty")
    with col2:
        # Placeholder for other buttons
        st.button("🇺🇸 S&P 500 (Coming Soon)")

# --- 4. PAGE: NIFTY 50 TABLE ---
elif st.session_state.page == "nifty":
    st.title("🇮🇳 Nifty 50 - Top 10 Leaders")
    if st.button("← Back to Home"): nav("home")
    
    # Fetch data for the table
    with st.spinner("Fetching latest market prices..."):
        try:
            # Download current data for all 10 tickers
            data = yf.download(NIFTY_TOP_10, period="5d", interval="1d")['Close']
            
            # Prepare rows for the table
            table_data = []
            for ticker in NIFTY_TOP_10:
                current_price = data[ticker].iloc[-1]
                prev_price = data[ticker].iloc[-2]
                pct_change = ((current_price - prev_price) / prev_price) * 100
                
                table_data.append({
                    "Symbol": ticker,
                    "Price (₹)": round(current_price, 2),
                    "Change %": f"{pct_change:+.2f}%"
                })
            
            # Display Table
            cols = st.columns([2, 2, 2, 2])
            cols[0].write("**Stock Symbol**")
            cols[1].write("**Current Price**")
            cols[2].write("**Daily Change**")
            cols[3].write("**Action**")
            
            st.markdown("---")
            for item in table_data:
                c1, c2, c3, c4 = st.columns([2, 2, 2, 2])
                c1.write(f"**{item['Symbol']}**")
                c2.write(f"₹{item['Price (₹)']:,}")
                
                # Color change text
                color = "#30d158" if "+" in item['Change %'] else "#ff453a"
                c3.markdown(f"<span style='color:{color}'>{item['Change %']}</span>", unsafe_allow_html=True)
                
                if c4.button("Analyze", key=item['Symbol']):
                    nav("detail", item['Symbol'])
                    
        except Exception as e:
            st.error(f"Error loading data: {e}")

# --- 5. PAGE: STOCK DETAIL (AI SUGGESTIONS) ---
elif st.session_state.page == "detail":
    t = st.session_state.ticker
    if st.button("← Back to List"): nav("nifty")
    
    df = yf.download(t, period="2y", progress=False)
    if not df.empty:
        # Remove multi-index if present
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        ltp = df['Close'].iloc[-1]
        st.title(f"Analysis: {t}")
        
        # --- AI SUGGESTION BOX ---
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        if ltp > ma50:
            status, sug, price, box = "Bullish", "Trading above 50-DMA. Uptrend is intact.", ma50 * 1.01, "suggestion-box"
        else:
            status, sug, price, box = "Cautious", "Price below 50-DMA. Wait for consolidation.", ma50 * 0.95, "suggestion-wait"

        st.markdown(f"""
            <div class="{box}">
                <h3>💡 Suggestion: {status}</h3>
                <p>{sug}</p>
                <h2>🎯 Suggested Entry: ₹{price:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

        # Simple Trend Chart
        fig = go.Figure(go.Scatter(x=df.index, y=df['Close'], line=dict(color='#007aff')))
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)