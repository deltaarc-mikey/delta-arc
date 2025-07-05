import streamlit as st
import os
from textblob import TextBlob
from openai import OpenAI

# Load OpenAI key securely
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

st.set_page_config(page_title="Strategy Replay + AI Summary", layout="wide")

# Title
st.title("📘 Strategy Replay Mode + Summary Comparison")

# GPT-4 Input
st.header("🧠 Generate GPT-4 Summary")
gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=150)

gpt_summary = ""
gpt_tone = ""
gpt_confidence = None

if st.button("Run GPT-4 Summary"):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional options trading analyst. Provide a one-paragraph summary of this trade and its logic."},
                {"role": "user", "content": gpt_input}
            ]
        )
        gpt_summary = response.choices[0].message.content.strip()
        st.subheader("📘 GPT-4 Summary:")
        st.write(gpt_summary)

        # GPT Tone + Confidence
        blob = TextBlob(gpt_summary)
        polarity = blob.sentiment.polarity
        gpt_tone = (
            "✅ Positive" if polarity > 0.3 else
            "❌ Negative" if polarity < -0.3 else
            "⚠️ Neutral"
        )
        keywords = ["breakout", "EMA", "MACD", "confirmation", "volume", "Reddit", "flow", "momentum", "timing", "profit"]
        hits = sum(1 for k in keywords if k.lower() in gpt_summary.lower())
        base_score = 50 + hits * 5 + polarity * 20
        gpt_confidence = round(min(max(base_score, 0), 100))
        score_emoji = "✅" if gpt_confidence > 80 else "🟡" if gpt_confidence > 60 else "🔴"
        st.success(f"**GPT Confidence Score: {score_emoji} {gpt_confidence}/100**")
        st.info(f"**GPT Tone:** {gpt_tone}")

    except Exception as e:
        st.error(f"GPT-4 summary generation failed:\n{e}")

# Claude Summary
with st.expander("📝 Claude Summary (Paste)"):
    claude_input = st.text_area("Paste Claude Summary")
    if st.button("Run Claude Summary"):
        if claude_input:
            st.subheader("Claude Summary Tone Detection:")
            blob = TextBlob(claude_input)
            polarity = blob.sentiment.polarity
            claude_tone = (
                "✅ Positive" if polarity > 0.3 else
                "❌ Negative" if polarity < -0.3 else
                "⚠️ Neutral"
            )
            st.success(f"Claude Summary Tone: {claude_tone}")
        else:
            st.warning("Please paste the Claude summary.")

# Summary Comparison
if gpt_summary and claude_input:
    st.header("📊 Claude vs GPT Summary Comparison")
    st.subheader("Claude Summary:")
    st.write(claude_input)
    st.subheader("GPT-4 Summary:")
    st.write(gpt_summary)

    st.markdown("---")
    st.subheader("🔍 Verdict:")
    if gpt_summary.strip() == claude_input.strip():
        st.success("✅ Summaries match. Strategy logic confirmed.")
    else:
        st.warning("⚠️ Differences detected. Review manually for alignment on strategy logic.")

    st.info("Claude and GPT tone comparison shown above. Use this to finalize trade archive.")
