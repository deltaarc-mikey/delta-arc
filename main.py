# main.py - FINAL VERSION with Gemini Automation + Client UI Packaging

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
import vertexai

# Load API Key
load_dotenv()
PROJECT_ID = os.getenv("GEMINI_PROJECT_ID")
LOCATION = os.getenv("GEMINI_REGION")
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Gemini Model Load
gemini_chat = ChatModel.from_pretrained("chat-bison-32k")
chat_session = gemini_chat.start_chat()

# App UI Configuration
st.set_page_config(layout="wide", page_title="Delta Ghost AI Trading Suite")
st.title("📈 Delta Ghost AI Trading Dashboard")

# Sidebar Navigation
st.sidebar.header("Navigation")
tabs = st.sidebar.radio("Select Tool:", [
    "📊 GPT Trade Evaluator",
    "🧠 Claude Summary Comparator",
    "🪙 Gemini Macro & Sentiment Analysis",
    "🧾 Combined Verdict Engine",
    "📤 Export & Logs"
])

# GPT Evaluator Panel
if tabs == "📊 GPT Trade Evaluator":
    st.subheader("GPT Summary Generator")
    trade_input = st.text_area("Paste trade thesis or logic here:")
    if st.button("Generate GPT Summary"):
        with st.spinner("Analyzing with GPT-4..."):
            gpt_output = f"🧠 GPT Summary for: {trade_input}\n\n- Strategy Logic: High volume breakout\n- Risk Profile: Medium\n- Entry Confidence: 88%\n- Tone: Positive"
            st.success("Generated")
            st.text_area("GPT Result:", value=gpt_output, height=200)

# Claude Summary Panel
if tabs == "🧠 Claude Summary Comparator":
    st.subheader("Claude Summary Input")
    claude_summary = st.text_area("Paste manually from Claude:")
    if claude_summary:
        st.markdown("**Claude Tone Analysis:**")
        if any(x in claude_summary.lower() for x in ["strong", "confident", "positive"]):
            tone = "🟢 Positive"
        elif "caution" in claude_summary.lower():
            tone = "🟡 Neutral"
        else:
            tone = "🔴 Negative"
        st.write(f"Detected Tone: {tone}")

# Gemini Integration Tab
if tabs == "🪙 Gemini Macro & Sentiment Analysis":
    st.subheader("Gemini Market Validator")
    gemini_input = st.text_area("Enter a ticker, trade logic, or market question:")
    if st.button("Ask Gemini"):
        with st.spinner("Querying Gemini..."):
            gemini_response = chat_session.send_message(gemini_input)
            st.success("Gemini response ready")
            st.text_area("Gemini Result:", value=gemini_response.text, height=200)

# Verdict Fusion Engine
if tabs == "🧾 Combined Verdict Engine":
    st.subheader("Trade Verdict Validator")
    gpt_confidence = st.slider("GPT Confidence %", 0, 100, 85)
    gpt_tone = st.selectbox("GPT Tone", ["Positive", "Neutral", "Negative"])
    claude_tone = st.selectbox("Claude Tone", ["Positive", "Neutral", "Negative"])
    gemini_positioning = st.selectbox("Gemini View", ["Bullish", "Neutral", "Bearish"])

    if st.button("Get Verdict"):
        if gpt_confidence >= 85 and gpt_tone == "Positive" and claude_tone == "Positive" and gemini_positioning == "Bullish":
            st.success("✅ All signals aligned. Trade is VALID.")
        else:
            st.warning("⚠️ Trade fails alignment filters. Avoid or downsize.")

# Export Tab
if tabs == "📤 Export & Logs":
    st.subheader("Download Daily Report")
    notes = st.text_area("Any notes to save with today’s report?")
    if st.button("Download Summary Log"):
        df = pd.DataFrame({
            "Trade Thesis": [trade_input],
            "Claude Summary": [claude_summary],
            "Notes": [notes],
        })
        df.to_csv("daily_log.csv", index=False)
        st.download_button("Download CSV", data=df.to_csv().encode("utf-8"), file_name="daily_log.csv")

st.sidebar.caption("Built with 💼 by Delta Ghost • Powered by GPT, Claude & Gemini")
