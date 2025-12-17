import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & CSS (Includes PWA & Mobile Optimizations) ---
st.set_page_config(
    page_title="FinQuest Pro",
    layout="wide",
    page_icon="💹",
    initial_sidebar_state="collapsed" # Collapsed for mobile-first
)

st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
    /* Base Dark Theme & Font */
    .stApp { background-color: #000000; color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto; }
    
    /* Remove default Streamlit padding */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    /* Landing Page Specific */
    .landing-title { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 1rem; color: #007AFF; }
    .creator-intro { font-size: 1.1rem; text-align: center; color: #E5E5EA; margin-bottom: 2rem; }
    .landing-card {
        background: rgba(28, 28, 30, 0.7);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .landing-card-title { font-size: 1.5rem; font-weight: 600; color: white; margin-bottom: 0.5rem; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; font-size: 1.1em;
        background-color: #1C1C1E; border: 1px solid #38383a;
        color: white; transition: all 0.2s;
    }
    .stButton>button:active { transform: scale(0.98); background-color: #2c2c2e; }

    /* General Stock Page Elements */
    [data-testid="stMetric"] {
        background: rgba(28, 28, 30, 0.8); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 15px !important; backdrop-filter: blur(10px);
    }
    h1 { font-size: 1.8rem !important; font-weight: 800 !important; margin-bottom: 0px !important; }
    .stCaption { font-size: 0.9rem !important; color: #8E8E93 !important; }
    iframe { width: 100% !important; }

    /* Sidebar specific for mobile */
    section[data-testid="stSidebar"] { 
        background-color: #1c1c1e !important; border-right: 1px solid #38383a; 
        width: 300px !important; 
        transition: transform 0.3s ease-in-out; /* Smooth sidebar transition */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"
if "history" not in st.session_state:
    st.session_state.history = ["landing"] # For back navigation

def navigate_to(page_name, ticker=None):
    if page_name not in st.session_state.history:
        st.session_state.history.append(page_name)
    st.session_state.page = page_name
    if ticker:
        st.session_state.selected_ticker = ticker
    st.rerun()

def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop() # Remove current page
        st.session_state.page = st.session_state.history[-1] # Go to previous
        st.rerun()

# --- 3. HELPER FUNCTIONS ---
def fetch_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data
    except: return None

# Index & Global Stock Lists
index_groups = {
    "🇮🇳 NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "ITC.NS"],
    "🌐 Global Top": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "BRK-B"],
    "🪙 Crypto & Commodities": ["BTC-USD", "ETH-USD", "GC=F"]
}
market_indices = {
    "NIFTY 50": "^NSEI", "SENSEX": "^BSESN", "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "FTSE 100": "^FTSE"
}

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://i.ibb.co/L5hS05r/finquest-pro-logo.png", use_column_width=True) # Your logo/app icon
    st.title("FinQuest Navigation")

    st.button("🏠 Home", on_click=navigate_to, args=("landing",), use_container_width=True)
    if st.session_state.page != "landing":
        st.button("⬅️ Back", on_click=go_back, use_container_width=True)
    st.markdown("---")

    st.subheader("Explore Markets")
    for group_name, tickers in index_groups.items():
        with st.expander(f"**{group_name}**"):
            for t in tickers:
                if st.button(f"{t}", key=f"side_nav_{t}"):
                    navigate_to("stock_detail", t)

# --- LANDING PAGE ---
if st.session_state.page == "landing":
    st.markdown('<p class="landing-title">FinQuest Pro</p>', unsafe_allow_html=True)
    
    # Image Generation for the creator (dynamic and inspiring)
    
    st.image("https://image.pollinations.ai/prompt/An%20epic%20digital%20artwork%20of%20a%20futuristic%20financial%20analyst%2C%20Krishna%2C%20with%20glowing%20holographic%20stock%20charts%20and%20data%20flowing%20around%20him%2C%20in%20a%20dark%20high-tech%20trading%20room%2C%20with%20a%20wise%20and%20determined%20expression%2C%20cyberpunk%20financial%20magic%2C%20volumetric%20lighting%2C%20intricate%20details", caption="Krishna, Creator of FinQuest Pro", use_column_width=True)
    
    st.markdown("""
        <p class="creator-intro">
            Namaste! I'm Krishna, the architect behind FinQuest Pro. 
            My vision was to create a stock analysis tool that’s not just powerful, but intuitive and elegantly designed for everyone, 
            right from your pocket. Dive in and experience the markets with clarity.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="landing-card-title">Quick Access</div>', unsafe_allow_html=True)
    
    # Grid for Quick Access to Major Indices/Groups
    major_links_cols = st.columns(2)
    with major_links_cols[0]:
        if st.button("📈 Global Top Stocks"):
            navigate_to("stock_list_page", "🌐 Global Top")
    with major_links_cols[1]:
        if st.button("🇮🇳 Nifty 50 Constituents"):
            navigate_to("stock_list_page", "🇮🇳 NIFTY 50")
    
    st.markdown('<div class="landing-card-title" style="margin-top:1.5rem;">Major Market Indices</div>', unsafe_allow_html=True)
    index_cols = st.columns(2)
    for i, (name, ticker_sym) in enumerate(market_indices.items()):
        with index_cols[i % 2]:
            idx_data = fetch_data(ticker_sym, period="2d", interval="1d")
            if idx_data is not None and len(idx_data) >= 2:
                current_close = idx_data['Close'].iloc[-1]
                prev_close = idx_data['Close'].iloc[-2]
                change = ((current_close / prev_close) - 1) * 100
                color = "#30d158" if change >= 0 else "#ff453a"
                st.markdown(f"""
                    <div class="landing-card">
                        <div style="font-weight: 600; font-size: 1.1em; color: white;">{name}</div>
                        <div style="font-size: 0.9em; color: {color};">{change:+.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="landing-card">{name} - Data Unavailable</div>', unsafe_allow_html=True)


# --- STOCK LIST PAGE (Dynamic list of tickers from an index/group) ---
elif st.session_state.page == "stock_list_page":
    group_key = st.session_state.get("current_group_key", "🌐 Global Top") # Default if none set
    
    # Try to determine group key from history (if navigated from landing page)
    if st.session_state.history[-1] == "landing" and st.session_state.page == "stock_list_page":
        # This is a bit tricky to extract if `navigate_to` only passed "stock_list_page"
        # Let's assume the calling button from landing page sets "current_group_key"
        pass # The navigate_to function will handle it by passing a `ticker` which is the group name in this case
        
    group_name_from_state = next((k for k, v in index_groups.items() if k == st.session_state.selected_ticker), "Stocks")
    st.title(f"{group_name_from_state} List")

    stocks_to_show = index_groups.get(st.session_state.selected_ticker, []) # Use selected_ticker as group_key
    
    if not stocks_to_show:
        st.warning("No stocks found for this group.")
    else:
        cols_per_row = 2 # For mobile-friendly grid
        cols = st.columns(cols_per_row)
        for i, ticker_sym in enumerate(stocks_to_show):
            with cols[i % cols_per_row]:
                stock_data = fetch_data(ticker_sym, period="1d", interval="1m")
                if stock_data is not None and len(stock_data) >= 2:
                    ltp = stock_data['Close'].iloc[-1]
                    prev_close = stock_data['Close'].iloc[-2]
                    change_pct = ((ltp / prev_close) - 1) * 100
                    color = "#30d158" if change_pct >= 0 else "#ff453a"
                    
                    st.markdown(f"""
                        <div class="landing-card">
                            <div style="font-weight: 600; color: white;">{ticker_sym}</div>
                            <div style="font-size: 0.9em; color: {color};">{change_pct:+.2f}%</div>
                            <div style="font-size: 0.8em; color: #8E8E93;">₹{ltp:,.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View {ticker_sym} Details", key=f"view_{ticker_sym}"):
                        navigate_to("stock_detail", ticker_sym)
                else:
                    st.markdown(f'<div class="landing-card">{ticker_sym} - Data N/A</div>', unsafe_allow_html=True)


# --- STOCK DETAIL PAGE (Your existing detailed stock viewer) ---
elif st.session_state.page == "stock_detail":
    current_ticker = st.session_state.selected_ticker
    st.title(f"📈 {current_ticker}")
    
    main_data = fetch_data(current_ticker, period="5d", interval="1d")

    if main_data is not None and len(main_data) >= 2:
        info = yf.Ticker(current_ticker).info # Re-fetch info as stock_obj is not persistent
        ltp = main_data['Close'].iloc[-1]
        prev = main_data['Close'].iloc[-2]
        change = ltp - prev
        pct = (change / prev) * 100
        
        col_price, _ = st.columns([2, 1])
        with col_price:
            st.metric("Current Price", f"{info.get('currency', '₹')}{ltp:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")

        time_frame = st.segmented_control("Range", options=["1D", "1M", "1Y", "5Y"], default="1Y")
        if not time_frame: time_frame = "1Y" # Default value protection
        
        c_period = time_frame.lower()
        c_interval = "2m" if time_frame == "1D" else "1d"
        chart_data = fetch_data(current_ticker, period=c_period, interval=c_interval)

        if chart_data is not None:
            line_color = "#30d158" if pct >= 0 else "#ff453a"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_data.index, y=chart_data['Close'], mode='lines',
                line=dict(color=line_color, width=3),
                fill='tozeroy',
                fillcolor=f"rgba({(48 if pct >= 0 else 255)}, {(209 if pct >= 0 else 69)}, {(88 if pct >= 0 else 58)}, 0.1)",
                hovertemplate="Price: %{y:.2f}<extra></extra>"
            ))
            fig.update_layout(
                template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black",
                height=400, margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, color="#8e8e93"),
                yaxis=dict(side="right", gridcolor="#2c2c2e", color="#8e8e93"),
                hovermode="x unified"
            )
            st.plotly_chart(fig, width='stretch')

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Day High", f"{ltp:,.2f}")
        m2.metric("Day Low", f"{main_data['Low'].iloc[-1]:,.2f}")
        m3.metric("Mkt Cap", f"{info.get('marketCap', 0)/1e12:.2f}T")
        m4.metric("PE Ratio", f"{info.get('trailingPE', 'N/A')}")
        
        with st.expander("🔔 Set Price Notification"):
            c_alt1, c_alt2 = st.columns(2)
            target = c_alt1.number_input("Target Price", value=float(ltp))
            u_email = c_alt2.text_input("Email Address")
            if st.button("Activate Alert", key="detail_alert_btn"):
                st.toast(f"Alert set for {current_ticker} at {target}", icon="✅")

    else:
        st.error(f"⚠️ Market data for {current_ticker} is currently unavailable. Try a different ticker.")