import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("📉 Strategy Replay Mode + Batch Backtest Loop")

# Load base chart data
csv_file_path = "AAPL_Strategy_Replay_Enhanced.csv"
if file is not None:
    df = pd.read_csv(file, parse_dates=["Date"])
    df["Date"] = pd.to_datetime(df["Date"])
else:
    st.warning("Please upload a CSV file to proceed.")
    st.stop()
df.set_index("Date", inplace=True)

# Sidebar: Strategy Replay Controls
st.sidebar.header("🕹️ Strategy Replay")
replay_mode = st.sidebar.radio("Replay Mode", ["Manual Step", "Auto Play"])
start_index = st.sidebar.slider("Start from row", 0, len(df)-1, 0)
replay_speed = st.sidebar.slider("Speed (sec)", 0.1, 2.0, 0.5)

# Sidebar: Batch Backtest Upload
st.sidebar.header("📄 Upload Batch Backtest File")
batch_file = st.sidebar.file_uploader("Upload CSV with Trade Signals", type=["csv"])

# --- Strategy Replay UI ---
st.subheader("🔁 Strategy Replay Mode")

if replay_mode == "Manual Step":
    step = st.number_input("Step forward by N rows", min_value=1, value=5)
    if st.button("Step"):
        preview_df = df.iloc[start_index:start_index+step]
        st.line_chart(preview_df["Close"])
elif replay_mode == "Auto Play":
    auto_length = st.number_input("Replay N steps", 10, 100, 20)
    if st.button("Play"):
        for i in range(start_index, min(start_index + auto_length, len(df))):
            st.line_chart(df.iloc[start_index:i]["Close"])
            time.sleep(replay_speed)

# --- Batch Backtest UI ---
st.subheader("📊 Batch Backtest Results")

if batch_file:
    try:
        batch_df = pd.read_csv(batch_file)
        st.write("✅ Uploaded Trades")
        st.dataframe(batch_df)

        # Backtest processing
        results = []
        for _, row in batch_df.iterrows():
            ticker = row['ticker']
            entry_date = pd.to_datetime(row['entry_date'])
            exit_date = pd.to_datetime(row['exit_date'])

            if entry_date in df.index and exit_date in df.index:
                entry = df.loc[entry_date]['Close']
                exit = df.loc[exit_date]['Close']
                pnl = round((exit - entry) / entry * 100, 2)
                results.append({
                    "ticker": ticker,
                    "entry_date": entry_date,
                    "exit_date": exit_date,
                    "entry_price": entry,
                    "exit_price": exit,
                    "PnL (%)": pnl
                })

        if results:
            result_df = pd.DataFrame(results)
            st.success("✅ Backtest Complete")
            st.dataframe(result_df)
            st.line_chart(result_df["PnL (%)"])
        else:
            st.warning("No valid trades found in date range.")

    except Exception as e:
        st.error(f"❌ Error in backtest: {e}")
