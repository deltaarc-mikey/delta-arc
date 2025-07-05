import streamlit as st
import pandas as pd

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("📉 Delta Ghost Backtesting Center")

# Sidebar selection for backtesting mode
mode = st.sidebar.selectbox("Select Backtest Mode", ["Basic Price", "Options Contract", "LLM Output Comparison"])

if mode == "Basic Price":
    st.header("📊 Price Movement Backtest")
    ticker = st.text_input("Ticker Symbol", "AAPL")
    entry_price = st.number_input("Entry Price", min_value=0.0, value=100.0)
    exit_price = st.number_input("Exit Price", min_value=0.0, value=110.0)
    notes = st.text_area("Trade Notes")

    if st.button("Run Price Backtest"):
        percent_return = ((exit_price - entry_price) / entry_price) * 100
        st.success(f"Trade Return: {percent_return:.2f}%")
        result_df = pd.DataFrame({
            "Ticker": [ticker],
            "Entry": [entry_price],
            "Exit": [exit_price],
            "Return %": [round(percent_return, 2)],
            "Notes": [notes]
        })
        st.dataframe(result_df)

elif mode == "Options Contract":
    st.header("🧾 Options Contract Backtest")
    ticker = st.text_input("Ticker Symbol", "TSLA")
    strike_price = st.number_input("Strike Price", min_value=0.0)
    stock_price_at_expiry = st.number_input("Stock Price at Expiry", min_value=0.0)
    option_type = st.radio("Option Type", ["Call", "Put"])
    notes = st.text_area("Test Notes")

    if st.button("Run Options Backtest"):
        if option_type == "Call":
            result = "ITM" if stock_price_at_expiry > strike_price else "OTM"
        else:
            result = "ITM" if stock_price_at_expiry < strike_price else "OTM"

        result_df = pd.DataFrame({
            "Ticker": [ticker],
            "Strike": [strike_price],
            "Expiry Price": [stock_price_at_expiry],
            "Option Type": [option_type],
            "Result": [result],
            "Notes": [notes]
        })
        st.success(f"Option Result: {result}")
        st.dataframe(result_df)

elif mode == "LLM Output Comparison":
    st.header("🧠 Claude vs ChatGPT vs Gemini Review")
    claude_output = st.text_area("Claude Output")
    gpt_output = st.text_area("ChatGPT Output")
    gemini_output = st.text_area("Gemini Output")
    trade_result = st.text_input("Final Trade Result (e.g. +35%, -10%)")
    notes = st.text_area("Comparison Notes")

    if st.button("Run Comparison Summary"):
        result_df = pd.DataFrame({
            "Claude": [claude_output],
            "ChatGPT": [gpt_output],
            "Gemini": [gemini_output],
            "Result": [trade_result],
            "Notes": [notes]
        })
        st.success("LLM analysis recorded.")
        st.dataframe(result_df)
