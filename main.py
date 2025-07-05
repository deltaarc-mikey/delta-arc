
import streamlit as st
from textblob import TextBlob
import openai
import os
import requests

st.set_page_config(page_title="Delta Ghost: AI Trade Engine", layout="wide")

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Sidebar navigation
st.sidebar.title("📊 Delta Ghost Control Panel")
tabs = ["📈 Trade Generator", "📡 Trend Scanner", "📘 Strategy Replay", "🧠 Verdict Hub"]
page = st.sidebar.radio("Navigate", tabs)

# --- GPT Summary Generator ---
def generate_gpt_summary(gpt_input):
    try:
        messages = [
            {"role": "system", "content": "You are a financial analyst specializing in options trading."},
            {"role": "user", "content": f"Summarize this trade idea. Rate the confidence 1–100 and describe tone:\n{gpt_input}"}
        ]
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- Claude Summary Tone Detector ---
def detect_tone(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

# --- Gemini Mock Sentiment Fuser (Replace with real logic/API as needed) ---
def gemini_sentiment_fusion(ticker):
    import random
    score = random.randint(40, 90)
    source = random.choice(["Reddit Buzz", "Google Trend", "Both"])
    return f"{score} ({source})"

# --- Strategy Replay GPT Summary ---
def simulate_trade_summary(trade_notes):
    return generate_gpt_summary(trade_notes)

# --- Verdict Comparator ---
def verdict(gpt_summary, claude_summary):
    gpt_tone = detect_tone(gpt_summary)
    claude_tone = detect_tone(claude_summary)
    aligned = gpt_tone == claude_tone
    return aligned, gpt_tone, claude_tone

# --- Layouts ---
if page == "📈 Trade Generator":
    st.title("📈 AI-Powered Trade Generator")

    gpt_input = st.text_area("📥 Paste your trade idea / batch", height=200)
    if st.button("🧠 Generate GPT-4 Summary"):
        gpt_summary = generate_gpt_summary(gpt_input)
        st.subheader("🧠 GPT-4 Summary")
        st.write(gpt_summary)

    claude_input = st.text_area("📥 Paste Claude Summary", height=150)
    if st.button("🧠 Run Claude Tone Analysis"):
        tone = detect_tone(claude_input)
        st.success(f"Claude Tone: {tone}")

    if gpt_input and claude_input:
        gpt_summary = generate_gpt_summary(gpt_input)
        verdict_result, gpt_t, claude_t = verdict(gpt_summary, claude_input)
        st.markdown("---")
        st.subheader("🧠 GPT vs Claude Verdict")
        st.write(f"**GPT Tone:** {gpt_t}")
        st.write(f"**Claude Tone:** {claude_t}")
        st.success("✅ Verdict: ALIGNED") if verdict_result else st.error("❌ Verdict: MISMATCH")

elif page == "📡 Trend Scanner":
    st.title("📡 Sentiment Trend Scanner")
    ticker = st.text_input("Enter Ticker Symbol")
    if ticker:
        score = gemini_sentiment_fusion(ticker.upper())
        st.info(f"📊 Sentiment Fusion Score for {ticker.upper()}: {score}")

elif page == "📘 Strategy Replay":
    st.title("📘 Strategy Replay: Backtest a Trade")
    past_trade = st.text_area("📥 Paste Historical Trade Notes", height=200)
    if st.button("🎞️ Simulate Summary"):
        result = simulate_trade_summary(past_trade)
        st.subheader("📈 Replay Summary")
        st.write(result)

elif page == "🧠 Verdict Hub":
    st.title("🧠 Final Summary Comparator")
    col1, col2, col3 = st.columns(3)

    with col1:
        gpt_block = st.text_area("Paste GPT-4 Summary", height=200)
    with col2:
        claude_block = st.text_area("Paste Claude Summary", height=200)
    with col3:
        gemini_score = st.text_input("Gemini Fusion Score")

    if st.button("🔎 Compare All"):
        tone_gpt = detect_tone(gpt_block)
        tone_claude = detect_tone(claude_block)
        match = tone_gpt == tone_claude
        st.subheader("🧠 Tone Verdict")
        st.write(f"**GPT Tone:** {tone_gpt}")
        st.write(f"**Claude Tone:** {tone_claude}")
        st.write(f"**Gemini Fusion Score:** {gemini_score}")
        st.success("✅ All LLMs Aligned") if match else st.warning("⚠️ Tones Diverge – Use Caution")
