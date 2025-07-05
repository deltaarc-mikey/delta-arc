# main.py — Delta Ghost Backtesting + Replay

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import openai
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("📊 Delta Ghost: Backtest & Replay + GPT/Claude Review")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

# --- Claude Manual Output ---
claude_output = st.text_area("Paste Claude Output Here for Comparison")

# --- GPT API Setup ---
openai.api_key = st.secrets.get("OPENAI_API_KEY")

# --- Real-time GPT Analysis ---
gpt_result = None
if st.button("Run GPT Summary") and uploaded_file:
    df = pd.read_csv(uploaded_file)
    prompt = f"""
You are a professional financial analyst. Review this 10-day candlestick data:
{df.to_string(index=False)}

Summarize the price movement, identify key levels, and give a recommendation for next steps based on this pattern.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional financial analyst."},
                {"role": "user", "content": prompt},
            ]
        )
        gpt_result = response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"GPT API error: {e}")

# --- Data Display and Replay ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])

    st.subheader("📈 Candlestick Chart")
    fig = go.Figure(data=[
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlesticks')
    ])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔁 Strategy Replay: Step Through Candles")
    start = st.slider("Select starting index", 0, len(df)-2, 0)
    next_day = start + 1 if start + 1 < len(df) else len(df)-1
    replay_df = df.iloc[:next_day+1]

    fig_replay = go.Figure(data=[
        go.Candlestick(
            x=replay_df['Date'],
            open=replay_df['Open'],
            high=replay_df['High'],
            low=replay_df['Low'],
            close=replay_df['Close'],
            name='Replay')
    ])
    st.plotly_chart(fig_replay, use_container_width=True)

    # --- P&L Heatmap ---
    st.subheader("📊 Profit Heatmap + Cumulative P&L")
    df['Daily Return'] = df['Close'].pct_change().fillna(0)
    df['Cumulative P&L'] = (1 + df['Daily Return']).cumprod()

    fig_pl = go.Figure()
    fig_pl.add_trace(go.Scatter(x=df['Date'], y=df['Cumulative P&L'], mode='lines+markers', name='Cumulative P&L'))
    fig_pl.update_layout(title="Cumulative Return Over Time", xaxis_title="Date", yaxis_title="Return")
    st.plotly_chart(fig_pl, use_container_width=True)

    # --- Heatmap Visual ---
    st.write("Heatmap of Daily Returns")
    heat_df = df.pivot_table(values='Daily Return', columns=df['Date'].dt.strftime('%Y-%m-%d'), aggfunc='sum')
    plt.figure(figsize=(12, 1))
    sns.heatmap(heat_df, cmap='RdYlGn', annot=True, fmt=".2%")
    st.pyplot(plt.gcf())

    # --- GPT vs Claude Side-by-Side ---
    st.subheader("🧠 GPT vs Claude Comparison")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Claude Summary (Manual Paste)**")
        st.text_area("Claude Result", claude_output, height=300)

    with col2:
        st.markdown("**GPT Live Summary**")
        st.write(gpt_result if gpt_result else "Click 'Run GPT Summary' to generate")

else:
    st.info("Please upload a CSV file to start the backtest and replay.")
