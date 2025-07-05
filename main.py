import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime
import openai
import os

# --- Set up page ---
st.set_page_config(page_title="Backtest & Replay", layout="wide")
st.title("📊 Strategy Backtest + Replay Mode")

# --- Upload CSV File ---
st.sidebar.header("📁 Upload Trade CSV")
csv_file = st.sidebar.file_uploader("Upload your trades file", type=["csv"])

# --- Inputs ---
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

# --- API Keys ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Helper Function: Load Data ---
def load_trade_data(file):
    df = pd.read_csv(file)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

# --- Backtest Engine ---
def run_backtest(df):
    results = []
    for index, row in df.iterrows():
        try:
            symbol = row['ticker']
            entry = pd.to_datetime(row['entry_date'])
            exit = pd.to_datetime(row['exit_date'])
            entry_price = float(row['entry_price'])
            target = float(row['target'])
            stop = float(row['stop'])

            hist = yf.download(symbol, start=entry.strftime('%Y-%m-%d'), end=exit.strftime('%Y-%m-%d'))
            hist = hist.reset_index()
            breached = ""
            for i, r in hist.iterrows():
                if r['Low'] <= stop:
                    breached = "Stop Hit"
                    break
                elif r['High'] >= target:
                    breached = "Target Hit"
                    break
            final_price = hist.iloc[-1]['Close'] if not hist.empty else entry_price
            pl = final_price - entry_price
            results.append({
                "ticker": symbol,
                "entry": entry.strftime('%Y-%m-%d'),
                "exit": exit.strftime('%Y-%m-%d'),
                "P/L": round(pl, 2),
                "Final Price": round(final_price, 2),
                "Target Breach": breached if breached else "None"
            })
        except Exception as e:
            st.warning(f"⚠️ Error on row {index + 1}: {e}")
    return pd.DataFrame(results)

# --- Replay Mode ---
def strategy_replay(ticker, entry, exit):
    data = yf.download(ticker, start=entry, end=exit)
    if data.empty:
        st.error("No data found. Check ticker or date range.")
        return
    data = data.reset_index()

    for i in range(len(data)):
        replay = data.iloc[:i+1]
        fig = go.Figure(data=[go.Candlestick(
            x=replay['Date'],
            open=replay['Open'],
            high=replay['High'],
            low=replay['Low'],
            close=replay['Close']
        )])
        fig.update_layout(title=f"{ticker} Strategy Replay – Day {i+1}/{len(data)}")
        st.plotly_chart(fig)
        if i < len(data) - 1:
            st.info("Use Next Step button to continue.")
            if not st.button("▶ Next Candle"):
                break

# --- GPT Summary Prompt ---
def summarize_trade_log(trade_df):
    prompt = "Summarize the following trade results in layman's terms and suggest one improvement:\n\n"
    prompt += trade_df.to_string(index=False)
    return prompt

# --- Claude Summary Prompt ---
def prepare_claude_prompt(trade_df):
    return f"""You are Claude, a trade analyst. Here is a table of trades:

{trade_df.to_string(index=False)}

Give a human-friendly analysis, focusing on which signals worked and which failed, and how to improve."""

# --- Main UI ---
if csv_file:
    trades_df = load_trade_data(csv_file)
    st.subheader("📋 Trade Log Preview")
    st.dataframe(trades_df)

    if st.button("Run Backtest"):
        with st.spinner("Running backtest..."):
            results = run_backtest(trades_df)
            st.success("✅ Backtest complete!")
            st.dataframe(results)

            # Visualization
            st.subheader("📈 Profit Heatmap")
            fig = go.Figure(data=go.Heatmap(
                z=results['P/L'],
                x=results['ticker'],
                y=results['entry'],
                colorscale='RdYlGn',
                colorbar_title="P/L"
            ))
            st.plotly_chart(fig)

            st.subheader("📈 Cumulative P/L")
            results['Cumulative P/L'] = results['P/L'].cumsum()
            st.line_chart(results['Cumulative P/L'])

            # GPT Analysis
            if st.button("🧠 Run GPT-4 Summary"):
                try:
                    prompt = summarize_trade_log(results)
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    output = response.choices[0].message.content
                    st.subheader("GPT-4 Summary")
                    st.write(output)
                except Exception as e:
                    st.error(f"GPT Error: {e}")

            # Claude Prompt
            if st.button("📤 Generate Claude Prompt"):
                prompt = prepare_claude_prompt(results)
                st.subheader("Claude Prompt")
                st.code(prompt)

    # Strategy Replay
    st.sidebar.header("🎬 Strategy Replay")
    symbol = st.sidebar.text_input("Ticker for Replay", value="AAPL")
    entry_date = st.sidebar.date_input("Replay Start Date", value=datetime(2024, 1, 3))
    exit_date = st.sidebar.date_input("Replay End Date", value=datetime(2024, 1, 9))
    if st.sidebar.button("Start Replay"):
        strategy_replay(symbol, entry_date.strftime("%Y-%m-%d"), exit_date.strftime("%Y-%m-%d"))
