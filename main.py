import streamlit as st
import pandas as pd
import openai
import re

# Set page config
st.set_page_config(page_title="Delta Ghost – Unified AI Dashboard", layout="wide")
st.title("🧠 Delta Ghost – Unified AI Trading Suite")

# Tabs
validator_tab, sentiment_tab, replay_tab, optimizer_tab, claude_tab = st.tabs([
    "✅ Trade Validator", "📊 Sentiment Fusion", "📁 Replay Engine", "⚙️ Optimizer", "🛠️ Claude Prompt Tuner"
])

# =============== TRADE VALIDATOR TAB ===============
with validator_tab:
    st.header("✅ LLM Trade Validator")
    gpt_input = st.text_area("📥 GPT Summary Prompt Input", height=150)
    claude_input = st.text_area("📥 Claude Summary Text (Paste manually)", height=150)
    run = st.button("▶️ Run GPT Summary")

    if run and gpt_input:
        with st.spinner("Analyzing with GPT..."):
            openai.api_key = st.secrets["OPENAI_API_KEY"]
            gpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"Summarize this trade idea. Rate the confidence 1–100 and describe tone: {gpt_input}"}
                ]
            )
            gpt_text = gpt_response["choices"][0]["message"]["content"]

            score_match = re.search(r"(Confidence|Score).*?(\d{1,3})", gpt_text, re.IGNORECASE)
            tone_match = re.search(r"(Tone|Sentiment).*?:?\s*(\w+)", gpt_text, re.IGNORECASE)
            score = int(score_match.group(2)) if score_match else "N/A"
            tone = tone_match.group(2).capitalize() if tone_match else "N/A"

            # Claude tone
            claude_tone = "Neutral"
            if "positive" in claude_input.lower():
                claude_tone = "Positive"
            elif "negative" in claude_input.lower():
                claude_tone = "Negative"

            # Score fusion
            if score != "N/A" and claude_tone == "Positive" and tone == "Positive":
                auto_score = "✅ STRONG ENTRY"
            elif score != "N/A" and "Neutral" in [claude_tone, tone]:
                auto_score = "⚠️ MODERATE"
            else:
                auto_score = "❌ AVOID"

            df = pd.DataFrame([{
                "Ticker": "Manual Input",
                "GPT Confidence Score": score,
                "GPT Tone": tone,
                "Claude Tone": claude_tone,
                "Auto Score": auto_score
            }])
            st.dataframe(df)

# =============== SENTIMENT FUSION TAB ===============
with sentiment_tab:
    st.header("📊 Sentiment Fusion Panel")
    st.markdown("_Coming soon: Pull Reddit + Google + Gemini trend fusion_ 🧠")
    st.info("This tab will show spike analysis from Reddit, Google Trends, and Gemini for early trade ideas.")

# =============== REPLAY ENGINE TAB ===============
with replay_tab:
    st.header("📁 Strategy Replay Mode")
    st.markdown("Upload a CSV of 50–100 historical trade setups. We'll simulate LLM outputs and score accuracy.")
    st.markdown("Example format: `Ticker, Strategy, Expiry, Result (Win/Loss)`")
    st.info("Coming soon: CSV ingestion, prompt simulation, backtest summary.")

# =============== OPTIMIZER TAB ===============
with optimizer_tab:
    st.header("⚙️ Strategy Optimizer")
    st.markdown("Paste any trade setup and GPT will suggest better spreads, expiries, or entries.")
    setup = st.text_area("Paste strategy (e.g., TSLA call debit spread exp 7/12 @ 0.42)")
    if st.button("🚀 Optimize Strategy"):
        with st.spinner("Querying GPT..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"Given this strategy, how can we optimize expiry or strike? Suggest better structure: {setup}"}
                ]
            )
            st.success("Suggestion:")
            st.write(response["choices"][0]["message"]["content"])

# =============== CLAUDE TUNER TAB ===============
with claude_tab:
    st.header("🛠️ Claude Prompt Tuner")
    st.markdown("Select tone profile to create reusable Claude prompts.")
    tone = st.selectbox("🎯 Choose Claude Tone Style", ["Quant-style", "Retail Buzz", "Neutral Analyst"])
    if tone:
        prompt = ""
        if tone == "Quant-style":
            prompt = "Summarize this options trade like a hedge fund quant. Prioritize data, math, and volatility edge."
        elif tone == "Retail Buzz":
            prompt = "Explain this trade like a Reddit meme stock pro. Use slang and excitement."
        else:
            prompt = "Summarize this trade in neutral tone with risk/reward and probability balance."

        st.code(prompt, language="text")

# Footer
st.markdown("---")
st.caption("Delta Ghost AI Suite © 2025 – Powered by GPT & Claude")
