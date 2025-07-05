import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from datetime import datetime

# Optional: Set your OpenAI API key
# openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="📘 Strategy Replay Mode + Batch Backtest", layout="wide")
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# Sidebar – Upload files
st.sidebar.header("📈 Upload Historical Price Data (CSV)")
price_file = st.sidebar.file_uploader("Upload price CSV", type=["csv"], key="price_file")

st.sidebar.header("📊 Upload Trade Log Data (CSV)")
trade_file = st.sidebar.file_uploader("Upload trades CSV", type=["csv"], key="trade_file")

# Read uploaded files
df_price = None
df_trades = None

if price_file is not None:
    df_price = pd.read_csv(price_file)
    st.success("✅ Price CSV uploaded successfully.")
    st.dataframe(df_price.head())

if trade_file is not None:
    df_trades = pd.read_csv(trade_file)
    st.success("✅ Trades CSV uploaded successfully.")
    st.dataframe(df_trades.head())

# Prevent running if both not uploaded
if df_price is None or df_trades is None:
    st.warning("Please upload both price and trade CSV files to continue.")
    st.stop()

# Convert Date column to datetime
df_price['Date'] = pd.to_datetime(df_price['Date'])
df_trades['entry_date'] = pd.to_datetime(df_trades['entry_date'])
df_trades['exit_date'] = pd.to_datetime(df_trades['exit_date'])

# Strategy Replay Logic
st.subheader("▶️ Replay & Backtest Engine")

results = []
errors = []

for index, trade in df_trades.iterrows():
    try:
        ticker = trade['ticker']
        entry = trade['entry_date']
        exit = trade['exit_date']
        target = trade['target_gain']

        mask = (df_price['Date'] >= entry) & (df_price['Date'] <= exit)
        df_segment = df_price.loc[mask]

        breached = any(df_segment['High'] >= target)
        breach_date = df_segment[df_segment['High'] >= target]['Date'].min() if breached else None

        entry_price = df_segment.iloc[0]['Open']
        final_price = df_segment.iloc[-1]['Close']
        pnl = round(final_price - entry_price, 2)

        results.append({
            'Trade': index + 1,
            'Ticker': ticker,
            'Entry': entry.date(),
            'Exit': exit.date(),
            'Entry Price': entry_price,
            'Exit Price': final_price,
            'P/L': pnl,
            'Target Breached': breached,
            'Breach Date': breach_date.date() if breach_date else "N/A"
        })

    except Exception as e:
        errors.append(f"⚠️ Error on row {index + 1}: {str(e)}")

# Display results
if results:
    df_results = pd.DataFrame(results)
    st.success("✅ Backtest complete!")
    st.dataframe(df_results)

    # Profit Heatmap
    st.subheader("📉 Profit Heatmap")
    try:
        fig, ax = plt.subplots()
        sns.heatmap(df_results[['P/L']], annot=True, cmap="RdYlGn", fmt=".2f", linewidths=0.5)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"⚠️ Heatmap failed: {e}")

    # Cumulative P&L
    st.subheader("📈 Cumulative P&L Over Time")
    try:
        df_results['Cum P/L'] = df_results['P/L'].cumsum()
        fig2, ax2 = plt.subplots()
        df_results.plot(x='Exit', y='Cum P/L', ax=ax2)
        st.pyplot(fig2)
    except Exception as e:
        st.error(f"⚠️ Plotting error: {e}")

# Error reporting
if errors:
    for err in errors:
        st.warning(err)

# GPT Summarization (placeholder for now)
st.subheader("🧠 GPT Trade Summary (Optional)")
if st.button("Generate GPT Summary"):
    prompt = "Summarize the backtest results below:\n\n" + df_results.to_csv(index=False)
    
    with st.spinner("Generating summary with GPT-4..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional trading analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            summary = response['choices'][0]['message']['content']
            st.markdown("### GPT-4 Summary")
            st.write(summary)
        except Exception as e:
            st.error(f"⚠️ GPT summarization failed: {e}")
