import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

st.set_page_config(page_title="Strategy Replay Mode + Batch Backtest Loop", layout="wide")
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# Upload CSV
st.subheader("📤 Upload Historical Price Data (CSV)")
st.caption("Upload a CSV with columns: Date, Open, High, Low, Close, Volume")
uploaded_file = st.file_uploader("Upload your historical CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    st.success("CSV uploaded successfully.")
    st.write(df.head())
    st.line_chart(df['Close'])

    st.download_button("📥 Download AAPL_Test_Historical.csv", uploaded_file, file_name="AAPL_Test_Historical.csv")

# Batch Backtest
st.subheader("🔄 Batch Multi-Trade Backtest Loop")
trade_input = st.text_area("Paste trades (comma-separated values: entry_date, exit_date, target_gain %)",
"""2025-06-05,2025-06-12,5
2025-06-13,2025-06-20,8
2025-06-21,2025-07-01,12""")

if st.button("Run Batch Backtest"):
    trades = []
    for i, line in enumerate(trade_input.strip().split('\n')):
        parts = line.strip().split(',')
        if len(parts) == 3:
            try:
                entry_date = pd.to_datetime(parts[0])
                exit_date = pd.to_datetime(parts[1])
                target = float(parts[2])
                entry_price = df.loc[entry_date]['Close']
                exit_price = df.loc[exit_date]['Close']
                return_pct = (exit_price - entry_price) / entry_price * 100
                target_hit = return_pct >= target
                trades.append({
                    "Trade": i,
                    "Entry Date": entry_date.date(),
                    "Exit Date": exit_date.date(),
                    "Target %": target,
                    "Entry Price": entry_price,
                    "Exit Price": exit_price,
                    "Return %": round(return_pct, 2),
                    "Target Hit": "✅ Yes" if target_hit else "❌ No"
                })
            except Exception as e:
                st.warning(f"⚠️ Error on row {i + 1}: {str(e)}")
    if trades:
        zresults = pd.DataFrame(trades)
        st.success("✅ Backtest complete!")
        st.dataframe(zresults)
        st.download_button("📥 Download Backtest Results", zresults.to_csv(index=False), file_name="backtest_results.csv")

        # Heatmap
        st.subheader("📉 Profit Heatmap")
        try:
            fig, ax = plt.subplots(figsize=(8, 3))
            sns.heatmap(zresults[['Return %']].T, cmap="RdYlGn", annot=True, fmt=".2f", cbar=False, ax=ax)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Heatmap error: {str(e)}")

        # Cumulative P/L
        st.subheader("📈 Cumulative P/L")
        zresults['Cum P/L'] = zresults['Return %'].cumsum()
        fig2, ax2 = plt.subplots()
        ax2.plot(zresults['Exit Date'], zresults['Cum P/L'], marker='o')
        ax2.set_ylabel("Cumulative % Return")
        ax2.set_title("Portfolio Growth Over Time")
        st.pyplot(fig2)

# Strategy Replay Mode Placeholder
st.subheader("⏪ Strategy Replay Mode (Coming Soon)")
st.info("Strategy Replay will allow you to simulate alerts + actions step-by-step using historical data.")

# Claude/GPT Prompt Section
st.subheader("🧠 Claude LLM Prompt")
st.code("""
You are an AI trading analyst. Review the historical price data between 2025-06-05 and 2025-07-02.
Assume an entry on the first day and an exit on the last day. Report:
- Entry price, Exit price
- Percentage return
- If a gain of 15% was achieved at any point
- Simple technical notes (trend, price behavior)
""", language="markdown")
