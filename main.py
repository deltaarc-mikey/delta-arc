import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# ========================== CSV Upload Section ==========================
st.subheader("📤 Upload Historical Price Data (CSV)")
file = st.file_uploader("Upload a CSV with columns: Date, Open, High, Low, Close, Volume", type=["csv"])

if file:
    df = pd.read_csv(file)
    df.columns = [c.strip().capitalize() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    st.success("CSV uploaded successfully.")
    st.dataframe(df.head())

    fig, ax = plt.subplots()
    ax.plot(df['Date'], df['Close'])
    ax.set_title('Close Price Over Time')
    st.pyplot(fig)

# ========================== Batch Backtest Loop ==========================
    st.subheader("🌀 Batch Multi-Trade Backtest Loop")
    st.caption("Each row below represents a trade setup: Entry Date, Exit Date, Target Gain %")

    trade_input = st.text_area("Paste trades (comma-separated values: entry_date, exit_date, target_gain)",
        "2025-06-05,2025-06-12,5\n2025-06-13,2025-06-20,8\n2025-06-21,2025-07-01,12")

    if st.button("▶️ Run Batch Backtest"):
        lines = trade_input.strip().split("\n")
        results = []

        for i, line in enumerate(lines):
            entry_date, exit_date, target = line.split(',')
            entry_date = pd.to_datetime(entry_date)
            exit_date = pd.to_datetime(exit_date)
            target = float(target)

            entry_row = df[df['Date'] == entry_date]
            exit_row = df[df['Date'] == exit_date]

            if not entry_row.empty and not exit_row.empty:
                entry_price = entry_row['Close'].values[0]
                exit_price = exit_row['Close'].values[0]
                return_pct = ((exit_price - entry_price) / entry_price) * 100
                target_hit = "✅ Yes" if return_pct >= target else "❌ No"

                results.append({
                    'Trade': i,
                    'Entry Date': entry_date.date(),
                    'Exit Date': exit_date.date(),
                    'Target %': target,
                    'Entry Price': round(entry_price, 2),
                    'Exit Price': round(exit_price, 2),
                    'Return %': round(return_pct, 2),
                    'Target Hit': target_hit
                })

        if results:
            result_df = pd.DataFrame(results)
            st.dataframe(result_df)

            csv_download = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Backtest Results", csv_download, "backtest_results.csv", "text/csv")

# ========================== Strategy Replay Mode ==========================
    st.markdown("""
    <h3>⏪ Strategy Replay Mode</h3>
    <div style='color:#A0AEC0;'>
    Walk through each day of historical data to simulate candle-by-candle trade replay.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🚦 Start Strategy Replay"):
        replay_start = st.date_input("Replay Start Date", df['Date'].min().date())
        replay_end = st.date_input("Replay End Date", df['Date'].max().date())

        filtered = df[(df['Date'] >= pd.to_datetime(replay_start)) & (df['Date'] <= pd.to_datetime(replay_end))]

        replay_index = st.slider("Step through candles", 0, len(filtered)-1, 0)
        current_row = filtered.iloc[replay_index]

        st.write(f"🕒 Date: {current_row['Date'].date()} | Open: {current_row['Open']} | Close: {current_row['Close']} | High: {current_row['High']} | Low: {current_row['Low']}")

        fig2, ax2 = plt.subplots()
        ax2.plot(filtered['Date'][:replay_index+1], filtered['Close'][:replay_index+1])
        ax2.set_title('Replay Progress (Close Price)')
        st.pyplot(fig2)

# ========================== GPT + Claude Prompt ==========================
    st.subheader("🧠 Claude LLM Prompt")
    replay_prompt = f"""
You are an AI trading analyst. Review the historical price data between {replay_start} and {replay_end}.
Assume an entry on the first day and an exit on the last day. Report:
- Entry price, Exit price
- Percentage return
- If a gain of 15% was achieved at any point
- Simple technical notes (trend, price behavior)

Data Snapshot:
{filtered.to_string(index=False)}
"""
    st.code(replay_prompt, language='markdown')

else:
    st.info("Please upload a historical price CSV to begin.")
