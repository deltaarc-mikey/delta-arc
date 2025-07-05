import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
from datetime import datetime, timedelta

# --- Streamlit Config ---
st.set_page_config(layout="wide")
st.title("📈 Backtesting + Strategy Replay Dashboard")
st.sidebar.title("⚙️ Settings")

# --- Tabs ---
tab = st.sidebar.radio("Choose Feature", ["Backtest Trade", "Claude Prompt Input", "Strategy Replay"])

# --- Backtest Trade Tab ---
if tab == "Backtest Trade":
    st.header("📊 Backtest Single Trade")
    ticker = st.text_input("Enter Ticker:", "AAPL")
    entry_date = st.date_input("Entry Date:", datetime.today() - timedelta(days=30))
    exit_date = st.date_input("Exit Date:", datetime.today())
    backtest_type = st.radio("Backtest Type:", ["Basic Price", "% Gain Target"], horizontal=True)
    percent_gain = st.slider("Target Gain % (if applicable):", 1, 100, 20)

    if st.button("Run Backtest"):
        try:
            data = yf.download(ticker, start=entry_date - timedelta(days=5), end=exit_date + timedelta(days=5))
            entry_price = data.loc[str(entry_date)]["Close"]
            exit_price = data.loc[str(exit_date)]["Close"]
            gain = ((exit_price - entry_price) / entry_price) * 100

            st.subheader(f"📌 {ticker} Trade Summary")
            st.write(f"Entry Price: ${entry_price:.2f}")
            st.write(f"Exit Price: ${exit_price:.2f}")
            st.write(f"Total Return: **{gain:.2f}%**")

            # Plot with markers
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close'))
            fig.add_trace(go.Scatter(x=[entry_date], y=[entry_price], mode='markers', marker=dict(size=10, color='green'), name='Entry'))
            fig.add_trace(go.Scatter(x=[exit_date], y=[exit_price], mode='markers', marker=dict(size=10, color='red'), name='Exit'))
            fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error during backtest: {e}")

# --- Claude Prompt UI ---
elif tab == "Claude Prompt Input":
    st.header("🧠 Claude Output Review")
    claude_input = st.text_area("Paste Claude 3.7 Strategy or Signal:")

    if st.button("Summarize with ChatGPT"):
        try:
            import openai
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            chat_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst summarizing a Claude LLM trading signal."},
                    {"role": "user", "content": claude_input}
                ]
            )
            summary = chat_response["choices"][0]["message"]["content"]
            st.subheader("💬 ChatGPT Summary")
            st.write(summary)
        except Exception as e:
            st.error(f"Error using OpenAI: {e}")

# --- Strategy Replay Tab ---
elif tab == "Strategy Replay":
    st.header("🔁 Strategy Replay Mode")
    replay_ticker = st.text_input("Ticker:", "TSLA")
    replay_date = st.date_input("Historical Replay Date:", datetime.today() - timedelta(days=10))

    if st.button("Run Replay"):
        try:
            start = replay_date - timedelta(days=15)
            end = replay_date + timedelta(days=15)
            data = yf.download(replay_ticker, start=start, end=end)

            st.subheader(f"📆 Replay Snapshot on {replay_date}")
            snapshot = data.loc[:str(replay_date)].copy()
            current_price = snapshot.iloc[-1]['Close']
            st.write(f"Price at Replay Date: **${current_price:.2f}**")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'))
            fig.add_vline(x=pd.Timestamp(replay_date), line_width=2, line_dash="dash", line_color="orange")
            fig.update_layout(title=f"{replay_ticker} Replay Chart", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig)

            st.info("Use this to simulate trade decisions based on price action up to that day.")

        except Exception as e:
            st.error(f"Replay Error: {e}")
