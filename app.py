import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText

# --- 1. CONFIG & SESSION STATE ---
st.set_page_config(page_title="FinQuest Pro Terminal", layout="wide", page_icon="💹")

# Initialize Session States
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "Market Summary"
if "selected_stock" not in st.session_state: st.session_state.selected_stock = "RELIANCE"
if "user_email" not in st.session_state: st.session_state.user_email = ""

# --- 2. THE NAVIGATION ENGINE (FIXED) ---
def nav_to(page_name, stock_name=None):
    """Safely switches pages and updates selected stock."""
    st.session_state.page = page_name
    if stock_name:
        st.session_state.selected_stock = stock_name

# --- 3. THE EMAIL BOT (OPTIONAL) ---
def send_email_alert(ticker, price, target, receiver_email):
    # Requires a Gmail App Password set in Streamlit Secrets
    sender_email = "your-bot@gmail.com" 
    password = st.secrets.get("GMAIL_PASS", "") 
    
    if not password:
        return False # Silently fail if no password configured
        
    msg = MIMEText(f"Target Hit! {ticker} is at ₹{price}. Your target was ₹{target}.")
    msg['Subject'] = f"🚀 Stock Alert: {ticker}"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except:
        return False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.title("🔐 FinQuest Pro Access")
    if st.text_input("Access Key", type="password") == "invest2025":
        if st.button("Unlock"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("📟 Menu")
    # Using buttons for navigation instead of radio for better 'Click-to-Profile' flow
    st.button("📊 Market Summary", on_click=nav_to, args=("Market Summary",), use_container_width=True)
    st.button("📈 Stock Profile", on_click=nav_to, args=("Stock Profile",), use_container_width=True)
    st.divider()
    st.caption("Data: 1m Delayed Intraday")

# --- PAGE: MARKET SUMMARY ---
if st.session_state.page == "Market Summary":
    st.header("📊 Top Sector Leaders")
    sectors = {
        "Banking": ["HDFCBANK", "ICICIBANK", "SBIN"],
        "IT": ["TCS", "INFY", "WIPRO"],
        "Energy": ["RELIANCE", "ONGC"]
    }
    
    for sector, stocks in sectors.items():
        st.subheader(sector)
        cols = st.columns(len(stocks))
        for i, s in enumerate(stocks):
            with cols[i]:
                # CLICKABLE: Takes user to the Stock Profile page
                st.button(f"View {s}", key=f"btn_{s}", on_click=nav_to, args=("Stock Profile", s))

# --- PAGE: STOCK PROFILE ---
elif st.session_state.page == "Stock Profile":
    ticker = st.session_state.selected_stock
    st.header(f"📈 {ticker} Technical Profile")

    # 1-MINUTE INTRADAY DATA FETCH
    data = yf.download(f"{ticker}.NS", period="1d", interval="1m", progress=False)
    
    if not data.empty:
        # Fix for multi-index column names
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        ltp = float(data['Close'].iloc[-1])
        st.metric("Current Live Price", f"₹{ltp:,.2f}")

        # --- THE BUY ALERT & EMAIL SECTION ---
        st.divider()
        col1, col2, col3 = st.columns([2, 2, 1])
        email_id = col1.text_input("Your Email (Optional)", value=st.session_state.user_email)
        target = col2.number_input("Buy Price Alert (₹)", value=round(ltp*0.99, 2))
        
        if col3.button("Set Alert"):
            st.session_state.user_email = email_id
            if ltp <= target:
                st.toast(f"🚨 TARGET HIT! {ticker} is at ₹{ltp}", icon="🚀")
                st.balloons()
                send_email_alert(ticker, ltp, target, email_id)
            else:
                st.info("Monitoring... I will alert you once hit.")

        # --- THE TREND GRAPH (INTRADAY 1M) ---
        # Moving Average to show "Trendiness"
        data['TrendLine'] = data['Close'].rolling(window=15).mean()
        
        fig = go.Figure()
        # Area Chart (Live Price)
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], fill='tozeroy', 
                                 line=dict(color='#00d1b2', width=2), name="Live Price"))
        # Trend Line (MA15)
        fig.add_trace(go.Scatter(x=data.index, y=data['TrendLine'], 
                                 line=dict(color='#FF4B4B', width=2, dash='dot'), name="15m Trend"))
        
        fig.update_layout(template="plotly_dark", height=450, xaxis_title="Time (Today)", 
                          margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)

        # AI Suggestion
        st.info(f"💡 **Suggestion:** Buy {ticker} if price stays above its trend line (Red Dotted).")