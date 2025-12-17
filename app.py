import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PREMIUM DARK UI ---
st.set_page_config(page_title="FinQuest Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    section[data-testid="stSidebar"] { background-color: #1c1c1e !important; border-right: 1px solid #38383a; width: 350px !important; }
    .stMetric { background-color: #1c1c1e; border-radius: 10px; padding: 15px; border: 1px solid #38383a; }
    [data-testid="stMetricValue"] { color: white !important; font-size: 28px !important; }
    .stButton>button { width: 100%; background-color: transparent; color: white; border: none; border-bottom: 1px solid #38383a; text-align: left; padding: 15px 10px; }
    .stButton>button:hover { background-color: #2c2c2e; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE & SEARCH ---
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE.NS"

def search_stocks(query):
    try:
        search = yf.Search(query, max_results=5)
        return [{"symbol": q['symbol'], "display": f"{q['symbol']} - {q.get('shortname', '')}"} for q in search.quotes]
    except: return []

# --- 3. SIDEBAR (Watchlist & Heatmap) ---
with st.sidebar:
    st.title("FinQuest Pro")
    
    # Search
    sq = st.text_input("Search", placeholder="Company or Ticker...")
    if sq:
        results = search_stocks(sq)
        for r in results:
            if st.button(r['display'], key=f"search_{r['symbol']}"):
                st.session_state.selected_ticker = r['symbol']

    st.markdown("### 🔥 Market Heatmap")
    indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Nasdaq": "^IXIC"}
    for name, sym in indices.items():
        idx_data = yf.Ticker(sym).history(period="2d")
        if not idx_data.empty:
            change = ((idx_data['Close'].iloc[-1] / idx_data['Close'].iloc[-2]) - 1) * 100
            color = "#30d158" if change >= 0 else "#ff453a"
            st.markdown(f"{name} <span style='color:{color}; float:right;'>{change:+.2f}%</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("My Watchlist")
    for s in ["RELIANCE.NS", "TCS.NS", "AAPL", "NVDA", "TSLA", "ZOMATO.NS"]:
        if st.button(f"**{s}**"): st.session_state.selected_ticker = s

# --- 4. MAIN DASHBOARD ---
ticker = st.session_state.selected_ticker
stock = yf.Ticker(ticker)
data = stock.history(period="1y", interval="1d")

if not data.empty:
    info = stock.info
    ltp = data['Close'].iloc[-1]
    change = ltp - data['Close'].iloc[-2]
    pct = (change / data['Close'].iloc[-2]) * 100

    # Header Row
    st.title(info.get('longName', ticker))
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.metric("", f"{info.get('currency', '₹')}{ltp:,.2f}", f"{pct:+.2f}%")
    
    # AI Sentiment Gauge
    # RSI calculation for sentiment
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
    
    sentiment = "Bullish 🚀" if rsi > 55 else "Bearish 📉" if rsi < 45 else "Neutral ⚖️"
    c2.metric("Market Sentiment", sentiment, f"RSI: {rsi:.1f}")

    # --- 5. THE CHART ---
    res = st.segmented_control("Timeframe", options=["1D", "1M", "1Y", "5Y"], default="1Y")
    chart_data = stock.history(period=res.lower(), interval="1m" if res=="1D" else "1d")
    
    fig = go.Figure()
    line_color = "#30d158" if pct >= 0 else "#ff453a"
    fig.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'], mode='lines', 
                             line=dict(color=line_color, width=3), fill='tozeroy',
                             fillcolor=f"rgba({(48 if pct >= 0 else 255)}, {(209 if pct >= 0 else 69)}, {(88 if pct >= 0 else 58)}, 0.1)"))
    fig.update_layout(template="plotly_dark", plot_bgcolor="black", paper_bgcolor="black", 
                      height=400, margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False), yaxis=dict(side="right"))
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. FUNDAMENTALS (REVENUE VS EARNINGS) ---
    st.markdown("### 📊 Annual Financials")
    
    try:
        fin = stock.financials.T[['Total Revenue', 'Net Income']].dropna().head(4)
        fig_fin = px.bar(fin, barmode='group', template="plotly_dark", 
                         color_discrete_map={'Total Revenue': '#007aff', 'Net Income': '#30d158'})
        fig_fin.update_layout(plot_bgcolor="black", paper_bgcolor="black", height=300)
        st.plotly_chart(fig_fin, use_container_width=True)
    except:
        st.info("Detailed financials not available for this ticker.")

    # --- 7. RECOGNITION / ACTION ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏛️ About Company")
        st.write(info.get('summary', 'No summary available.'))
    with col_b:
        st.markdown("### 🛠️ Quick Tools")
        if st.button("🔔 Set Dynamic Price Alert"):
            st.toast(f"Monitoring {ticker} for volatility!", icon="🔥")
        st.download_button("📥 Export Historical Data (CSV)", data.to_csv(), "data.csv")