import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from datetime import datetime

# Set your GPT-4 API key here or use environment variable
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else "YOUR_API_KEY_HERE"

st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# Upload historical data CSV
st.subheader("📥 Upload Historical Price Data (CSV)")
price_csv = st.file_uploader("Upload your historical CSV", type=["csv"])

if price_csv:
    df = pd.read_csv(price_csv)
    if 'Date' not in df.columns:
        st.error("CSV must contain a 'Date' column.")
    else:
        df['Date'] = pd.to_datetime(df['Date'])
        st.success("CSV uploaded successfully.")
        st.dataframe(df.head())

# Upload trade backtest CSV
st.sidebar.header("📤 Upload Trade CSV")
trade_csv = st.sidebar.file_uploader("Upload your trades file", type=["csv"])
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime(2025, 7, 5))

results = []

if trade_csv and price_csv:
    trades_df = pd.read_csv(trade_csv)

    st.subheader("📊 Batch Backtest")
    st.dataframe(trades_df)

    for i, row in trades_df.iterrows():
        try:
            entry_date = pd.to_datetime(row['entry_date'])
            exit_date = pd.to_datetime(row['exit_date'])
            target_gain = float(row['target_gain'])

            entry_row = df[df['Date'] == entry_date]
            exit_row = df[df['Date'] == exit_date]

            if entry_row.empty or exit_row.empty:
                st.warning(f"⚠️ Error on row {i+1}: invalid entry or exit date")
                continue

            entry_price = entry_row['Close'].values[0]
            exit_price = exit_row['Close'].values[0]
            return_pct = ((exit_price - entry_price) / entry_price) * 100
            target_hit = return_pct >= target_gain

            results.append({
                'Trade': i,
                'Entry Date': entry_date.date(),
                'Exit Date': exit_date.date(),
                'Target %': target_gain,
                'Entry Price': round(entry_price, 2),
                'Exit Price': round(exit_price, 2),
                'Return %': round(return_pct, 2),
                'Target Hit': "✅ Yes" if target_hit else "❌ No"
            })

        except Exception as e:
            st.error(f"Error processing row {i+1}: {e}")

    if results:
        zresults = pd.DataFrame(results)
        st.success("✅ Backtest complete!")
        st.dataframe(zresults)

        # 📈 Profit Heatmap
        st.subheader("📉 Profit Heatmap")
        try:
            fig, ax = plt.subplots()
            sns.heatmap(zresults[['Return %']], annot=True, cmap='coolwarm', ax=ax)
            st.pyplot(fig)
        except KeyError:
            st.error("Error: Could not render heatmap. Check 'Return %' column.")

        # 📈 Cumulative P/L chart
        st.subheader("📈 Cumulative P/L")
        try:
            zresults['Cumulative P/L'] = zresults['Return %'].cumsum()
            fig2, ax2 = plt.subplots()
            zresults.plot(x='Trade', y='Cumulative P/L', ax=ax2, marker='o')
            st.pyplot(fig2)
        except Exception as e:
            st.error(f"Cumulative chart error: {e}")

        # 🤖 GPT Summarization
        st.subheader("🤖 GPT-4 Summarization (Trade Insights)")

        summarize_all = "".join([
            f"Trade {r['Trade']}: Entry {r['Entry Date']}, Exit {r['Exit Date']}, Target {r['Target %']}%, Return {r['Return %']}% -> {r['Target Hit']}\n"
            for r in results
        ])

        if st.button("Summarize All Trades with GPT-4"):
            with st.spinner("Calling GPT-4..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an AI financial analyst. Summarize the trading performance."},
                            {"role": "user", "content": summarize_all}
                        ]
                    )
                    st.success("Response from GPT-4:")
                    st.markdown(response['choices'][0]['message']['content'])
                except Exception as e:
                    st.error(f"OpenAI Error: {e}")

else:
    st.info("Please upload both historical price CSV and trade CSV to begin.")
