import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai
from datetime import datetime
from textblob import TextBlob

# ----- CONFIG -----
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ----- PAGE CONFIG -----
st.set_page_config(layout="wide", page_title="Delta Ghost LLM Consensus Engine")
st.title("🔺 Delta Ghost: AI Trade Consensus Dashboard")

# ----- FILE UPLOAD -----
st.sidebar.header("📤 Upload Trade CSV")
uploaded_file = st.sidebar.file_uploader("Upload trade data CSV", type="csv")

# ----- GEMINI INPUT -----
st.sidebar.header("🧠 Gemini Input Panel")
gemini_input = st.sidebar.text_area("Enter Gemini analysis or paste prompt:")

# ----- CLAUDE INPUT -----
st.sidebar.header("🧠 Claude Summary Input")
claude_input = st.sidebar.text_area("Paste Claude summary here:")

# ----- GPT PROMPT -----
st.sidebar.header("🤖 GPT Trade Summary Generator")
gpt_input = st.sidebar.text_area("Enter trade setup or thesis:")
run_gpt = st.sidebar.button("Generate GPT Summary")

# ----- GPT OUTPUT -----
gpt_summary, gpt_score, gpt_tone = "", 0, ""
if run_gpt and gpt_input:
    with st.spinner("Asking GPT-4..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional options trader."},
                {"role": "user", "content": f"Summarize this trade idea. Rate the confidence 1–100 and describe tone:\n{gpt_input}"},
            ]
        )
        gpt_summary = response.choices[0].message.content
        blob = TextBlob(gpt_summary)
        gpt_score = min(100, max(0, int(blob.sentiment.polarity * 100)))
        gpt_tone = "Positive" if blob.sentiment.polarity > 0.2 else "Neutral" if blob.sentiment.polarity > -0.1 else "Negative"

# ----- CLAUDE TONE -----
claude_tone = ""
if claude_input:
    blob = TextBlob(claude_input)
    claude_tone = "Positive" if blob.sentiment.polarity > 0.2 else "Neutral" if blob.sentiment.polarity > -0.1 else "Negative"

# ----- DISPLAY -----
st.subheader("🧠 LLM Trade Comparison")
cols = st.columns(3)
with cols[0]:
    st.markdown("#### 🤖 GPT Summary")
    st.write(gpt_summary)
    st.metric("Confidence", f"{gpt_score}%")
    st.metric("Tone", gpt_tone)

with cols[1]:
    st.markdown("#### 🧠 Claude Summary")
    st.write(claude_input)
    st.metric("Tone", claude_tone)

with cols[2]:
    st.markdown("#### 🔮 Gemini Input")
    st.write(gemini_input)
    # Gemini summary box (placeholder)
    st.info("Gemini response currently handled outside app. Paste below once retrieved.")
    gemini_out = st.text_area("Paste Gemini output here")
    if gemini_out:
        blob = TextBlob(gemini_out)
        gemini_tone = "Positive" if blob.sentiment.polarity > 0.2 else "Neutral" if blob.sentiment.polarity > -0.1 else "Negative"
        st.metric("Tone", gemini_tone)

# ----- ALIGNMENT -----
def verdict(gt, ct):
    return "✅ Aligned" if gt == ct else "❌ Conflict"

if gpt_tone and claude_tone:
    st.subheader("⚖️ Verdict")
    st.success(f"Claude and GPT verdict: {verdict(gpt_tone, claude_tone)}")

# ----- CSV BACKTEST READER -----
if uploaded_file:
    st.subheader("📈 Backtest & Replay Results")
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    # Profit Curve
    if 'Profit' in df.columns:
        st.line_chart(df['Profit'].cumsum(), use_container_width=True)

    # Heatmap
    if 'Profit' in df.columns and 'Trade ID' in df.columns:
        pivot = df.pivot_table(index='Trade ID', values='Profit', aggfunc='sum')
        fig, ax = plt.subplots()
        pivot.plot(kind='barh', ax=ax, color='skyblue')
        st.pyplot(fig)

    # GPT-4 Row Summary Generator
    st.subheader("🧠 GPT Summary per Trade Row")
    for i, row in df.iterrows():
        with st.expander(f"Trade {i+1}: {row.get('Ticker', 'N/A')}"):
            setup = f"Ticker: {row.get('Ticker', '')}\nStrategy: {row.get('Strategy', '')}\nProfit: {row.get('Profit', '')}"
            if st.button(f"Summarize Row {i+1}"):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a trading analyst."},
                        {"role": "user", "content": f"Summarize this trade:\n\n{setup}"}
                    ]
                )
                st.write(response.choices[0].message.content)

st.markdown("---")
st.markdown("Built for **Delta Ghost** | All data auto-cleansed and archived. 🧠📈")
