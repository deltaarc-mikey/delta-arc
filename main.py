import streamlit as st
import pandas as pd
import io
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Strategy Replay Mode + Batch Backtest Loop", layout="wide")
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# Upload Historical CSV
st.subheader("📥 Upload Historical Price Data (CSV)")
st.caption("Upload a CSV with columns: Date, Open, High, Low, Close, Volume")
file = st.file_uploader("", type=["csv"])

if file:
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    st.success("CSV uploaded successfully.")
    st.dataframe(df.head())

    st.line_chart(df['Close'])

    st.download_button("📎 Download AAPL_Test_Historical.csv", file, file_name="AAPL_Test_Historical.csv")

# Backtest: Batch Input
st.subheader("🔄 Batch Multi-Trade Backtest Loop")
st.markdown("Each row below represents a trade setup: Entry Date, Exit Date, Target Gain %")
trade_input = st.text_area("Paste trades (comma-separated values: entry_date, exit_date, target_gain)",
    "2025-06-05,2025-06-12,5\n2025-06-13,2025-06-20,8\n2025-06-21,2025-07-01,12")

if st.button("▶️ Run Batch Backtest"):
    trade_lines = trade_input.strip().split("\n")
    trades = []
    for line in trade_lines:
        entry_date, exit_date, target_gain = line.split(",")
        entry_date = pd.to_datetime(entry_date)
        exit_date = pd.to_datetime(exit_date)
        target_gain = float(target_gain)
        if entry_date in df.index and exit_date in df.index:
            entry_price = df.loc[entry_date]['Close']
            exit_price = df.loc[exit_date]['Close']
            return_pct = ((exit_price - entry_price) / entry_price) * 100
            target_hit = return_pct >= target_gain
            trades.append({
                "Entry Date": entry_date.date(),
                "Exit Date": exit_date.date(),
                "Target %": target_gain,
                "Entry Price": round(entry_price, 2),
                "Exit Price": round(exit_price, 2),
                "Return %": round(return_pct, 2),
                "Target Hit": "✅ Yes" if target_hit else "❌ No"
            })
        else:
            st.error(f"Invalid date in: {line}")

    result_df = pd.DataFrame(trades)
    st.dataframe(result_df)
    csv_download = result_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Backtest Results", csv_download, "backtest_results.csv")

# Replay Mode UI
st.subheader("⏪ Strategy Replay Mode (Coming Soon)")
st.info("🔄 Strategy Replay will allow you to simulate alerts + actions step-by-step using historical data.")

# Claude LLM Prompt
st.subheader("🧠 Claude LLM Prompt")
st.code(
    """
You are an AI trading analyst. Review the historical price data between 2025-06-05 and 2025-07-02.
Assume an entry on the first day and an exit on the last day. Report:
- Entry price, Exit price
- Percentage return
- If a gain of 15% was achieved at any point
- Simple technical notes (trend, price behavior)
""".strip(), language='markdown')
