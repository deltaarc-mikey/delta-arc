import streamlit as st
import yfinance as yf
data = yf.download("MSFT", start="2024-11-15", end="2024-12-15")
print(data.head())
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objs as go

st.set_page_config(page_title="Backtest & Strategy Replay", layout="wide")

# -------------------------
# Helper: Visualize trade
# -------------------------
def visualize_trade(data, entry_date, exit_date):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines', name='Close Price',
        line=dict(color='lightblue')
    ))
    fig.add_trace(go.Scatter(
        x=[entry_date], y=[data.loc[entry_date]['Close']],
        mode='markers+text', name='Entry',
        marker=dict(color='green', size=12),
        text=["Entry"], textposition="bottom center"
    ))
    fig.add_trace(go.Scatter(
        x=[exit_date], y=[data.loc[exit_date]['Close']],
        mode='markers+text', name='Exit',
        marker=dict(color='red', size=12),
        text=["Exit"], textposition="top center"
    ))
    fig.update_layout(title="📈 Trade Visualization",
                      xaxis_title="Date",
                      yaxis_title="Price",
                      height=500)
    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# App Title
# -------------------------
st.title("📊 Backtesting + Strategy Replay Dashboard")
st.header("📈 Backtest Single Trade")

# -------------------------
# Input Fields
# -------------------------
ticker = st.text_input("Enter Ticker:", value="AAPL")
entry_date = st.text_input("Entry Date:", value="2025/06/17")
exit_date = st.text_input("Exit Date:", value="2025/07/01")
backtest_type = st.radio("Backtest Type:", ["Basic Price", "% Gain Target"])
gain_target = st.slider("Target Gain % (if applicable):", 1, 100, 75)

# -------------------------
# Backtest Logic
# -------------------------
if st.button("Run Backtest"):
    try:
        data = yf.download(ticker, start=entry_date, end=exit_date)
        data.index = pd.to_datetime(data.index)
        if data.empty:
            st.warning("⚠️ No data found. Check ticker or date range.")
        else:
            if backtest_type == "Basic Price":
                start_price = data.iloc[0]['Close']
                end_price = data.iloc[-1]['Close']
                percent_change = ((end_price - start_price) / start_price) * 100
                result = f"💹 From {entry_date} to {exit_date}, {ticker} changed by {percent_change:.2f}%"
                st.success(result)
                visualize_trade(data, data.index[0], data.index[-1])

            elif backtest_type == "% Gain Target":
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
                    visualize_trade(data, data.index[0], target_hit_date)
                else:
                    st.warning(f"❌ Target not hit between {entry_date} and {exit_date}.")
                    visualize_trade(data, data.index[0], data.index[-1])
    except Exception as e:
        st.error(f"Error during backtest: {e}")

# -------------------------
# Strategy Replay (Placeholder)
# -------------------------
st.header("⏮️ Strategy Replay Mode (Coming Soon)")
st.info("⚙️ Strategy Replay will allow you to simulate historical alerts and decisions step-by-step. Stay tuned!")

# -------------------------
# Claude Prompt Helper (Manual)
# -------------------------
st.header("🧠 Claude LLM Prompt")
st.markdown("""
    Paste this prompt into Claude (Sonnet 3.7) to get a historical trade summary:
""")
