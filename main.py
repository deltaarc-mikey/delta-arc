import streamlit as st
import os
from textblob import TextBlob
from openai import OpenAI

# Load API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

st.set_page_config(page_title="Strategy Replay + Summary Comparison", layout="wide")
st.title("📘 Strategy Replay Mode + Summary Comparison")

# ---- GPT-4 Summary Input ----
st.header("🧠 Generate GPT-4 Summary")
gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=150)
gpt_summary = ""
gpt_tone = ""
gpt_confidence = 0

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

        # Tone and confidence
        blob = TextBlob(gpt_summary)
        polarity = blob.sentiment.polarity
        gpt_tone = (
            "✅ Positive" if polarity > 0.3 else
            "❌ Negative" if polarity < -0.3 else
            "⚠️ Neutral"
        )
        keywords = ["breakout", "flow", "Reddit", "momentum", "confirmation", "reversal", "volume", "trend"]
        hits = sum(1 for k in keywords if k.lower() in gpt_summary.lower())
        base_score = 50 + hits * 5 + polarity * 20
        gpt_confidence = round(min(max(base_score, 0), 100))
        score_emoji = "✅" if gpt_confidence > 80 else "🟡" if gpt_confidence > 60 else "🔴"
        st.success(f"**GPT Confidence Score: {score_emoji} {gpt_confidence}/100**")
        st.info(f"**GPT Tone:** {gpt_tone}")

    except Exception as e:
        st.error(f"GPT-4 summary generation failed:\n\n{e}")

# ---- Claude Summary Input ----
claude_input = ""
claude_summary = ""
claude_tone = ""
with st.expander("📝 Claude Summary (Paste)", expanded=True):
    claude_input = st.text_area("Paste Claude Summary", key="claude_input", height=100)
    if st.button("Run Claude Summary"):
        if claude_input.strip():
            blob = TextBlob(claude_input)
            polarity = blob.sentiment.polarity
            claude_tone = (
                "✅ Positive" if polarity > 0.3 else
                "❌ Negative" if polarity < -0.3 else
                "⚠️ Neutral"
            )
            st.success(f"Claude Summary Tone: {claude_tone}")
            claude_summary = claude_input.strip()
        else:
            st.warning("Please paste a Claude summary.")

# ---- Comparison Section ----
if gpt_summary and claude_input:
    st.markdown("---")
    st.header("📊 Claude vs GPT Summary Comparison")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Claude Summary:")
        st.write(claude_input)
        blob = TextBlob(claude_input)
        cpol = blob.sentiment.polarity
        c_tone = (
            "✅ Positive" if cpol > 0.3 else
            "❌ Negative" if cpol < -0.3 else
            "⚠️ Neutral"
        )
        st.info(f"**Claude Tone:** {c_tone}")

    with col2:
        st.subheader("GPT-4 Summary:")
        st.write(gpt_summary)
        st.info(f"**GPT Tone:** {gpt_tone}")
        st.success(f"**GPT Confidence Score: {gpt_confidence}/100**")

    # Verdict Box
    st.markdown("---")
    st.subheader("🔍 Verdict:")
    if gpt_summary.strip() == claude_input.strip():
        st.success("✅ Summaries match. Strategy logic confirmed.")
    else:
        st.warning("⚠️ Differences detected. Review manually for alignment on strategy logic.")

    st.info("Claude and GPT tone comparison shown above. Use this tool to finalize trade review or archive insights.")
