import streamlit as st
import pandas as pd
import datetime as dt
import plotly.graph_objs as go

# Page config
st.set_page_config(page_title="Backtest + Strategy Replay", layout="wide")
st.title("📊 Backtesting + Strategy Replay Dashboard")

st.subheader("📈 Upload Historical Price Data (CSV)")

uploaded_file = st.file_uploader("Upload CSV with columns: Date, Open, High, Low, Close, Volume", type=["csv"])
data = None

ticker_list = []

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['Date'])
        df = df.sort_values("Date")
        df['Date'] = pd.to_datetime(df['Date'])
        ticker = uploaded_file.name.split('.')[0].upper()
        ticker_list.append(ticker)
        data = df
        st.success(f"✅ Successfully uploaded data for {ticker}")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")

# Divider
st.markdown("---")
st.subheader("📉 Backtest Single Trade")

if data is not None:
    selected_ticker = ticker_list[0]
    entry_date = st.date_input("Entry Date:", value=dt.date.today() - dt.timedelta(days=30))
    exit_date = st.date_input("Exit Date:", value=dt.date.today())
    backtest_type = st.radio("Backtest Type:", ["Basic Price", "% Gain Target"])
    target_gain = st.slider("Target Gain % (if applicable):", 1, 100, 25) if backtest_type == "% Gain Target" else None

    if st.button("🚀 Run Backtest"):
        try:
            df_bt = data.copy()
            df_bt = df_bt[(df_bt['Date'] >= pd.to_datetime(entry_date)) & (df_bt['Date'] <= pd.to_datetime(exit_date))]

            if df_bt.empty:
                st.warning("⚠️ No data found for the selected date range.")
            else:
                entry_price = df_bt.iloc[0]['Close']
                exit_price = df_bt.iloc[-1]['Close']

                result = {}
                result['Entry Price'] = entry_price
                result['Exit Price'] = exit_price
                result['Return %'] = ((exit_price - entry_price) / entry_price) * 100

                if backtest_type == "% Gain Target":
                    target_price = entry_price * (1 + target_gain / 100)
                    hit_target = (df_bt['Close'] >= target_price).any()
                    result['Target Gain %'] = target_gain
                    result['Target Hit?'] = "✅ Yes" if hit_target else "❌ No"

                st.markdown(f"### 📌 {selected_ticker} Trade Summary")
                st.json(result)

                # Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_bt['Date'], y=df_bt['Close'], mode='lines+markers', name='Close Price'))
                fig.update_layout(title=f"{selected_ticker} Price Chart", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"❌ Error during backtest: {e}")

# Divider for Replay Mode and Claude Prompt
st.markdown("---")
st.subheader("⏪ Strategy Replay Mode (Coming Soon)")
st.info("🔄 Strategy Replay will allow you to simulate historical alerts and decisions step-by-step. Stay tuned!")

st.subheader("🧠 Claude LLM Prompt")
st.markdown("Paste this prompt into Claude (Sonnet 3.7) to get a historical trade summary:")

if data is not None:
    cl_prompt = f"""
You are an AI trading analyst. Review the historical price data for {selected_ticker} between {entry_date} and {exit_date}. Assume an entry on the first day and an exit on the last day. Report:
- Entry price, Exit price
- Percentage return
- If a gain of {target_gain}% was achieved at any point (if applicable)
- Simple technical notes (trend, price behavior)
"""
    st.code(cl_prompt, language='markdown')
else:
    st.warning("⬆️ Upload CSV data above to generate prompt.")
