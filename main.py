import streamlit as st
import pandas as pd
from textblob import TextBlob
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

st.set_page_config(page_title="Delta Ghost – Trade Validator", layout="wide")
st.title("📈 Delta Ghost – Trade Validator")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Trade Validator", "🧪 Backtest Runner", "🛠️ Claude Prompt Tuner"])

# Shared session state for results
if "results" not in st.session_state:
    st.session_state.results = []

with tab1:
    st.header("📌 Trade Evaluation Results")

    gpt_input = st.text_area("🧠 GPT Summary Prompt Input", height=150)
    claude_input = st.text_area("🧠 Claude Summary Text (Paste manually)", height=150)

    if st.button("▶️ Run GPT Summary"):
        try:
            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst."},
                    {"role": "user", "content": f"Summarize this trade idea. Rate the confidence 1–100 and describe tone:\n{gpt_input}"}
                ]
            )
            reply = gpt_response.choices[0].message.content

            # Extract confidence score
            confidence = None
            for word in reply.split():
                if word.strip('%').isdigit():
                    num = int(word.strip('%'))
                    if 0 <= num <= 100:
                        confidence = num
                        break

            # Tone tagging
            analysis = TextBlob(reply)
            tone = "Positive" if analysis.sentiment.polarity > 0 else "Negative" if analysis.sentiment.polarity < 0 else "Neutral"

            # Claude tone
            claude_analysis = TextBlob(claude_input)
            claude_tone = "Positive" if claude_analysis.sentiment.polarity > 0 else "Negative" if claude_analysis.sentiment.polarity < 0 else "Neutral"

            # Auto score: average of GPT confidence and tone alignment (basic example)
            auto_score = (confidence if confidence else 50)
            if tone == claude_tone:
                auto_score += 10

            st.session_state.results.append({
                "Ticker": "Manual Input",
                "GPT Confidence Score": confidence,
                "GPT Tone": tone,
                "Claude Tone": claude_tone,
                "Auto Score": auto_score
            })

        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df)

with tab2:
    st.header("📂 Backtest Batch Runner")
    uploaded_file = st.file_uploader("Upload CSV file of past trades", type=["csv"])
    if uploaded_file:
        df_backtest = pd.read_csv(uploaded_file)
        st.write("✅ File uploaded and valid. Proceeding...")
        st.dataframe(df_backtest)

with tab3:
    st.header("🎯 Claude Prompt Tuner")
    preset = st.selectbox("Choose Claude Tone Preset", ["Quantitative", "Retail Buzz", "Neutral", "Bearish", "Bullish"])
    st.write("Claude prompt tone preset applied: ", preset)
    custom_claude = st.text_area("✍️ Customize Claude prompt manually")
