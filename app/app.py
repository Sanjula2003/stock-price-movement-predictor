import streamlit as st
import joblib

# Load model
model = joblib.load("../models/stock_movement_model.pkl")

# Page config
st.set_page_config(
    page_title="Stock Predictor",
    page_icon="📈",
    layout="centered"
)

# Title
st.title("📈 Stock Price Movement Predictor")

st.markdown("### Predict whether stock price may go UP or DOWN")

st.divider()

# Inputs
close_price = st.number_input("Close Price", value=150.0)

sma_10 = st.number_input("10-Day SMA", value=148.0)

rsi = st.number_input("RSI", value=55.0)

# Prediction button
if st.button("Predict Stock Movement"):

    input_data = [[close_price, sma_10, rsi]]

    prediction = model.predict(input_data)

    st.divider()

    if prediction[0] == 1:
        st.success("📈 Prediction: Stock Price May Go UP")
    else:
        st.error("📉 Prediction: Stock Price May Go DOWN")