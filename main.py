import streamlit as st
import openai
import os
from textblob import TextBlob

# Set your OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Strategy Replay + GPT Summary Tool", layout="wide")

# ---- HEADER ----
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# ---- Upload Sections ----
st.header("📅 Upload Historical Price Data (CSV)")
hist_csv = st.file_uploader("Upload your historical CSV", type="csv")

st.header("📈 Upload Trade History (CSV)")
trade_csv = st.file_uploader("Upload your trades CSV", type="csv")

# ---- GPT-4 Summary Section ----
st.header("🧠 Generate GPT-4 Summary")
gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=150)
gpt_summary = ""
gpt_confidence = None

if st.button("Run GPT-4 Summary"):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional trading analyst. Return a one-paragraph summary of the trade and rationale based on the following input."},
                {"role": "user", "content": gpt_input}
            ]
        )
        gpt_summary = response.choices[0].message.content.strip()
        st.subheader("📘 GPT-4 Summary:")
        st.write(gpt_summary)

        # ---- Confidence Scoring Logic ----
        keywords = ["breakout", "EMA", "MACD", "confirmation", "volume", "Reddit", "flow", "momentum"]
        keyword_hits = sum(1 for word in keywords if word.lower() in gpt_summary.lower())
        polarity = TextBlob(gpt_summary).sentiment.polarity  # -1 to 1

        base_score = 50 + (keyword_hits * 5) + (polarity * 20)
        gpt_confidence = round(min(max(base_score, 0), 100))  # Clamp between 0 and 100

        # ---- Score Display ----
        if gpt_confidence > 80:
            score_color = "✅"
        elif gpt_confidence > 60:
            score_color = "🟡"
        else:
            score_color = "🔴"
        st.success(f"**GPT Confidence Score: {score_color} {gpt_confidence}/100**")

    except Exception as e:
        st.error(f"GPT-4 summary generation failed:\n\n{str(e)}")

# ---- Claude Summary ----
with st.expander("📝 Claude Summary (Paste)", expanded=True):
    claude_input = st.text_area("Paste Claude Summary", height=100)
    claude_tone = ""
    if st.button("Run Claude Summary"):
        blob = TextBlob(claude_input)
        polarity = blob.sentiment.polarity
        if polarity > 0.3:
            tone = "✅ Positive"
        elif polarity < -0.3:
            tone = "❌ Negative"
        else:
            tone = "⚠️ Neutral"
        claude_tone = tone
        st.success(f"Claude Summary Tone: {tone}")
        st.info("Claude Summary stored and tagged. Use comparison box below to finalize GPT vs Claude review.")

# ---- Comparison ----
if gpt_summary and claude_input:
    st.header("📊 Claude vs GPT Summary Comparison")

    st.subheader("Claude Summary:")
    st.write(claude_input)

    st.subheader("GPT-4 Summary:")
    st.write(gpt_summary)

    # Auto Verdict Logic
    if claude_input and gpt_summary:
        if claude_input[:30] in gpt_summary or gpt_summary[:30] in claude_input:
            verdict = "✅ Alignment detected. Strategy logic consistent between GPT and Claude."
        else:
            verdict = "🕵️ Verdict: ⚠️ Differences detected. Review manually for alignment on strategy logic."
        st.markdown(f"**{verdict}**")

# ---- Footer Note ----
st.info("📦 Upload both historical price CSV and trade CSV to begin full backtest. Use GPT and Claude summaries to archive insights or identify future entry conditions.")
