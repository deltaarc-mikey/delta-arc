import streamlit as st
import pandas as pd
import openai
import os
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Delta Ghost Trade Validator", layout="wide")
st.title("📈 Delta Ghost – Trade Validator")

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_tone(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.15:
        return "Positive"
    elif polarity < -0.15:
        return "Negative"
    else:
        return "Neutral"

def auto_score(gpt_score, gpt_tone, claude_tone):
    score = 0
    if gpt_score >= 85:
        score += 40
    elif gpt_score >= 70:
        score += 25
    else:
        score += 10

    if gpt_tone == "Positive":
        score += 25
    elif gpt_tone == "Neutral":
        score += 10

    if claude_tone == "Positive":
        score += 25
    elif claude_tone == "Neutral":
        score += 10

    if gpt_tone == claude_tone:
        score += 10
    return min(score, 100)

st.sidebar.header("LLM Trade Input")
gpt_input = st.sidebar.text_area("🧠 GPT Summary Prompt Input", height=250)
claude_summary = st.sidebar.text_area("🧠 Claude Summary Text (Paste manually)", height=200)

gpt_summary = ""
gpt_score = None
gpt_tone = ""

if st.sidebar.button("🔍 Run GPT Summary"):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a trading assistant. Analyze trade ideas."},
            {"role": "user", "content": f"Summarize this trade idea. Rate the confidence 1–100 and describe tone:\n{gpt_input}"}
        ]
    )
    gpt_summary = response['choices'][0]['message']['content']
    st.subheader("📝 GPT Summary")
    st.write(gpt_summary)

    # Extract confidence score
    import re
    score_match = re.search(r'confidence.*?(\d+)', gpt_summary, re.IGNORECASE)
    if score_match:
        gpt_score = int(score_match.group(1))
    gpt_tone = analyze_tone(gpt_summary)

claude_tone = analyze_tone(claude_summary) if claude_summary else ""

# Auto Score
auto_scored = None
if gpt_score is not None and gpt_tone and claude_tone:
    auto_scored = auto_score(gpt_score, gpt_tone, claude_tone)

# Results Display
st.subheader("📊 Trade Evaluation Results")
results = {
    "Ticker": ["Manual Input"],
    "GPT Confidence Score": [gpt_score],
    "GPT Tone": [gpt_tone],
    "Claude Tone": [claude_tone],
    "Auto Score": [auto_scored]
}
df = pd.DataFrame(results)

required_cols = ['Ticker', 'GPT Confidence Score', 'GPT Tone', 'Claude Tone', 'Auto Score']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.warning(f"⚠️ Missing columns in output: {missing_cols}")
    st.dataframe(df)
else:
    st.dataframe(df[required_cols])

st.markdown("---")
st.caption("Delta Ghost AI Validator © 2025")
