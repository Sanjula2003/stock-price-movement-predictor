import streamlit as st
import joblib
import plotly.graph_objects as go
import yfinance as yf
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator

st.set_page_config(
    page_title="Stock Predictor",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}
div[data-baseweb="input"] input {
    background-color: #1E1E1E !important;
    color: white !important;
}
.stButton>button {
    background-color: #00C896;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}
.stButton>button:hover {
    background-color: #00E6AC;
    color: black;
}
</style>
""", unsafe_allow_html=True)

model = joblib.load("stock_movement_model.pkl")

st.title("📈 Stock Price Movement Predictor")
st.markdown("### Live Finance ML Dashboard for Buy/Sell Signal Prediction")

stock_options = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Meta": "META",
    "Netflix": "NFLX",
    "JPMorgan Chase": "JPM",
    "Coca-Cola": "KO"
}

selected_stock = st.selectbox("Select Stock", list(stock_options.keys()))
ticker = stock_options[selected_stock]

data = yf.download(ticker, period="1y", interval="1d")

if data.empty:
    st.error("No stock data found. Please check the ticker symbol or internet connection.")
    st.stop()

data["SMA_10"] = SMAIndicator(
    close=data["Close"].squeeze(),
    window=10
).sma_indicator()

data["RSI"] = RSIIndicator(
    close=data["Close"].squeeze(),
    window=14
).rsi()

data = data.dropna()

if data.empty:
    st.error("Not enough stock data to calculate indicators.")
    st.stop()

st.subheader(f"Latest Stock Data for {selected_stock} ({ticker})")
st.dataframe(data.tail(), use_container_width=True)

st.divider()

st.subheader("Market Summary")

latest_close = data["Close"].iloc[-1].item()
latest_high = data["High"].iloc[-1].item()
latest_low = data["Low"].iloc[-1].item()
latest_volume = data["Volume"].iloc[-1].item()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Close", f"${latest_close:.2f}")
col2.metric("High", f"${latest_high:.2f}")
col3.metric("Low", f"${latest_low:.2f}")
col4.metric("Volume", f"{latest_volume:,.0f}")

st.divider()

st.subheader("Technical Indicators")

latest_sma = data["SMA_10"].iloc[-1].item()
latest_rsi = data["RSI"].iloc[-1].item()

col1, col2 = st.columns(2)

col1.metric("SMA 10", f"{latest_sma:.2f}")
col2.metric("RSI", f"{latest_rsi:.2f}")

st.divider()

st.subheader("Candlestick Chart")

fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data["Open"].squeeze(),
    high=data["High"].squeeze(),
    low=data["Low"].squeeze(),
    close=data["Close"].squeeze()
)])

fig.update_layout(
    title=f"{selected_stock} ({ticker}) Candlestick Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="white"),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("ML Prediction Signal")

if st.button("Predict Stock Movement"):

    input_data = [[latest_close, latest_sma, latest_rsi]]

    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)

    up_probability = probability[0][1] * 100
    down_probability = probability[0][0] * 100

    if prediction[0] == 1:
        st.success("🟢 BUY SIGNAL")
        st.metric("Prediction Confidence", f"{up_probability:.2f}%")
    else:
        st.error("🔴 SELL SIGNAL")
        st.metric("Prediction Confidence", f"{down_probability:.2f}%")

    col1, col2 = st.columns(2)
    col1.metric("UP Probability", f"{up_probability:.2f}%")
    col2.metric("DOWN Probability", f"{down_probability:.2f}%")

    st.divider()

    st.subheader("Trend Analysis")

    if latest_close > latest_sma:
        st.success("📈 Bullish Trend Detected")
    elif latest_close < latest_sma:
        st.error("📉 Bearish Trend Detected")
    else:
        st.warning("⚖ Neutral Trend")

    st.subheader("RSI Market Condition")

    if latest_rsi > 70:
        st.warning("⚠️ Overbought Market Condition")
    elif latest_rsi < 30:
        st.warning("⚠️ Oversold Market Condition")
    else:
        st.info("✅ Neutral RSI Condition")

    st.subheader("Prediction Explanation")

    if latest_close > latest_sma:
        st.write("• Stock price is currently above the 10-Day SMA, indicating bullish momentum.")
    else:
        st.write("• Stock price is currently below the 10-Day SMA, indicating bearish pressure.")

    if latest_rsi > 70:
        st.write("• RSI indicates the stock may be overbought.")
    elif latest_rsi < 30:
        st.write("• RSI indicates the stock may be oversold.")
    else:
        st.write("• RSI indicates neutral market momentum.")