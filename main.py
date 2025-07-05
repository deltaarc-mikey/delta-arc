import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="Strategy Replay Mode + Batch Backtest", layout="wide")

st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# Upload CSV file
st.subheader("📤 Upload Historical Price Data (CSV)")
file = st.file_uploader("Upload a CSV with columns: Date, Open, High, Low, Close, Volume", type=["csv"])

if file is not None:
    df = pd.read_csv(file, parse_dates=["Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    st.success("CSV uploaded successfully.")
    st.write(df.head())

    # Display basic chart
    st.line_chart(df.set_index("Date")["Close"])

    st.divider()

    # Batch backtest logic
    st.subheader("🌀 Batch Multi-Trade Backtest Loop")

    st.info("Each row below represents a trade setup: Entry Date, Exit Date, Target Gain %")

    batch_data = st.text_area(
        "Paste trades (comma-separated values: entry_date, exit_date, target_gain)",
        value="2025-06-05,2025-06-12,5\n2025-06-13,2025-06-20,8\n2025-06-21,2025-07-01,12"
    )

    if st.button("▶️ Run Batch Backtest"):
        batch_results = []
        lines = batch_data.strip().split("\n")
        for i, line in enumerate(lines):
            try:
                entry_str, exit_str, target_str = line.split(",")
                entry = pd.to_datetime(entry_str.strip())
                exit = pd.to_datetime(exit_str.strip())
                target = float(target_str.strip())

                trade_df = df[(df["Date"] >= entry) & (df["Date"] <= exit)]

                if trade_df.empty:
                    result = {"Trade": i+1, "Error": "No data in date range"}
                else:
                    entry_price = trade_df.iloc[0]["Close"]
                    exit_price = trade_df.iloc[-1]["Close"]
                    percent_return = ((exit_price - entry_price) / entry_price) * 100
                    hit_target = any(
                        ((row["High"] - entry_price) / entry_price) * 100 >= target
                        for _, row in trade_df.iterrows()
                    )
                    result = {
                        "Trade": i+1,
                        "Entry Date": entry_str,
                        "Exit Date": exit_str,
                        "Target %": target,
                        "Entry Price": round(entry_price, 2),
                        "Exit Price": round(exit_price, 2),
                        "Return %": round(percent_return, 2),
                        "Target Hit": "✅ Yes" if hit_target else "❌ No"
                    }
                batch_results.append(result)
            except Exception as e:
                batch_results.append({"Trade": i+1, "Error": str(e)})

        result_df = pd.DataFrame(batch_results)
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Backtest Results", csv, "batch_backtest_results.csv", "text/csv")

    st.divider()

    # Strategy Replay Mode (stub)
    st.subheader("⏪ Strategy Replay Mode (Coming Soon)")
    st.info("🔄 Strategy Replay will allow you to simulate alerts + actions step-by-step using historical data.")

    st.divider()

    # Claude prompt
    st.subheader("🧠 Claude LLM Prompt")

    claude_prompt = f"""You are an AI trading analyst. Review the historical price data between {df['Date'].min().strftime('%Y-%m-%d')} and {df['Date'].max().strftime('%Y-%m-%d')}. 
Assume an entry on the first day and an exit on the last day. Report:
- Entry price, Exit price
- Percentage return
- If a gain of 15% was achieved at any point
- Simple technical notes (trend, price behavior)"""

    st.code(claude_prompt, language="markdown")

else:
    st.warning("Upload a valid CSV file to begin.")
