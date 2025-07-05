import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="Backtesting + Strategy Replay", layout="wide")

st.title("📉 Backtesting + Strategy Replay Dashboard")

st.header("📊 Backtest Single Trade")

ticker = st.text_input("Enter Ticker:", "AAPL")
entry_date = st.text_input("Entry Date:", "2025/06/17")
exit_date = st.text_input("Exit Date:", "2025/07/01")

backtest_type = st.radio("Backtest Type:", ["Basic Price", "% Gain Target"])
gain_target = st.slider("Target Gain % (if applicable):", 1, 100, 75)

run = st.button("Run Backtest")

def fetch_data(ticker):
    return yf.download(ticker, period="6mo", interval="1d")

def visualize_trade(data, entry_date, exit_date):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlesticks"
    ))

    fig.add_vline(x=pd.to_datetime(entry_date), line=dict(color='green', dash='dot'), annotation_text="Entry", annotation_position="top left")
    fig.add_vline(x=pd.to_datetime(exit_date), line=dict(color='red', dash='dot'), annotation_text="Exit", annotation_position="top right")

    st.plotly_chart(fig, use_container_width=True)

if run:
    try:
        data = fetch_data(ticker.upper())
        if data.empty:
            st.error("No data returned for ticker.")
        else:
            data.index = pd.to_datetime(data.index)
            entry_price = float(data.loc[entry_date]['Close'])
            exit_price = float(data.loc[exit_date]['Close'])
            gain = ((exit_price - entry_price) / entry_price) * 100

            visualize_trade(data, entry_date, exit_date)

            st.subheader(f"📌 {ticker.upper()} Trade Summary")
            if backtest_type == "% Gain Target":
    # Calculate percentage change daily from entry
    subset = data.loc[entry_date:exit_date]
    entry_price = float(subset.iloc[0]['Close'])
    target_price = entry_price * (1 + gain_target / 100)

    target_hit_date = None
    for date, row in subset.iterrows():
        if row['Close'] >= target_price:
            target_hit_date = date
            break

    if target_hit_date:
        result_str = f"🎯 Target hit on {target_hit_date.date()} — Price: ${row['Close']:.2f} — Gain: {(row['Close'] - entry_price)/entry_price*100:.2f}%"
        st.success(result_str)
        visualize_trade(data, entry_date, str(target_hit_date.date()))
    else:
        st.warning(f"❌ Target not hit between {entry_date} and {exit_date}.")
        visualize_trade(data, entry_date, exit_date)

    except Exception as e:
        st.error(f"Error during backtest: {e}")
