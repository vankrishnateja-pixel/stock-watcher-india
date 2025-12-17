import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Page Config (Sets the name in the browser tab)
st.set_page_config(page_title="InvestWise | Stock Watcher", layout="wide")

# 2. Sidebar Authentication (Simple)
with st.sidebar:
    st.title("🔑 Login")
    password = st.text_input("Enter Access Key", type="password")
    if password != "invest2025":
        st.warning("Please enter the correct key to see data.")
        st.stop()
    st.success("Access Granted!")

# 3. Main Header
st.title("📈 InvestWise Dashboard")
st.caption("Tracking Indian Markets with 15-min Delay")

# 4. Create Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["Stock Watcher", "Top Gainers (Demo)", "SIP Planner"])

with tab1:
    ticker = st.text_input("Enter NSE Ticker", "RELIANCE").upper()
    stock = yf.Ticker(f"{ticker}.NS")
    data = stock.history(period="1mo")
    
    if not data.empty:
        col1, col2 = st.columns([1, 3])
        ltp = data['Close'].iloc[-1]
        col1.metric("Current Price", f"₹{ltp:,.2f}", f"{((ltp/data['Close'].iloc[-2])-1)*100:.2f}%")
        
        fig = go.Figure(data=[go.Scatter(x=data.index, y=data['Close'], mode='lines', fill='tozeroy')])
        fig.update_layout(title=f"{ticker} 30-Day Trend", template="plotly_white", height=300)
        col2.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🚀 Today's Market Pulse")
    # Simple static list for Demo; you can automate this later
    st.write("Current High-Volume Gainers:")
    st.table({"Ticker": ["TATASTEEL", "ZOMATO", "ADANIENT"], "Change": ["+4.2%", "+3.8%", "+2.1%"]})

with tab3:
    st.subheader("🎯 Wealth Goal Calculator")
    amt = st.number_input("Monthly SIP Amount (₹)", 500, 100000, 5000)
    yrs = st.slider("Invest for how many years?", 1, 30, 10)
    # SIP Calculation Logic
    i = (12/100)/12 # 12% annual rate
    n = yrs * 12
    fv = amt * (((1 + i)**n - 1) / i) * (1 + i)
    st.success(f"At 12% growth, you'll have: **₹{fv:,.0f}**")
