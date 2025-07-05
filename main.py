import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from openai import OpenAI
import os

# --- Title ---
st.set_page_config(page_title="🧠 Strategy Replay Mode + GPT/Claude Batch Analysis")
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# --- API Setup ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- State Management ---
if "gpt_summary" not in st.session_state:
    st.session_state.gpt_summary = ""
if "claude_summary" not in st.session_state:
    st.session_state.claude_summary = ""

# --- File Uploads ---
st.subheader("📅 Upload Historical Price Data (CSV)")
price_file = st.file_uploader("Upload your historical CSV", type=["csv"], key="price")

st.subheader("📈 Upload Trade History (CSV)")
trade_file = st.file_uploader("Upload your trades CSV", type=["csv"], key="trades")

# --- GPT Summary ---
st.subheader("🧠 Generate GPT-4 Summary")
gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=200)
run_gpt = st.button("Run GPT-4 Summary")

if run_gpt and gpt_input:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Summarize the trade batch insightfully and concisely."},
                {"role": "user", "content": gpt_input}
            ]
        )
        gpt_summary = response.choices[0].message.content.strip()
        st.session_state.gpt_summary = gpt_summary
        st.subheader("📄 GPT-4 Summary:")
        st.markdown(gpt_summary)
    except Exception as e:
        st.error(f"❌ GPT-4 summary generation failed: {e}")

# --- Claude Summary (Manual Input) ---
with st.expander("📝 Claude Summary (Paste)"):
    claude_input = st.text_area("Paste Claude Summary", height=150)
    run_claude = st.button("Run Claude Summary")

    if run_claude and claude_input:
        # Claude tone/intent tagging
        with st.spinner("Analyzing Claude Summary..."):
            if any(word in claude_input.lower() for word in ["excellent", "perfect", "strong", "great", "high confidence"]):
                tone = "✅ Positive"
            elif any(word in claude_input.lower() for word in ["cautious", "decent", "mixed", "partial", "risk"]):
                tone = "⚠️ Neutral / Cautious"
            elif any(word in claude_input.lower() for word in ["bad", "avoid", "weak", "fail", "hype", "undisciplined", "loss"]):
                tone = "❌ Negative"
            else:
                tone = "🤔 Unknown"

            st.success(f"Claude Summary Tone: **{tone}**")
            st.info("Claude Summary stored and tagged. Use comparison box below to finalize GPT vs Claude review.")

# --- GPT vs Claude Comparison ---
if st.session_state.gpt_summary and st.session_state.claude_summary:
    st.subheader("📊 Claude vs GPT Summary Comparison")
    st.markdown("### Claude Summary:")
    st.markdown(st.session_state.claude_summary)
    st.markdown("### GPT-4 Summary:")
    st.markdown(st.session_state.gpt_summary)

    # Simple difference comparison
    if st.session_state.gpt_summary == st.session_state.claude_summary:
        verdict = "✅ Full agreement between GPT and Claude."
    else:
        verdict = "⚠️ Differences detected. Review manually for alignment on strategy logic."

    st.markdown(f"#### 🔍 Verdict: {verdict}")

# --- Instruction Footer ---
st.info("🔄 Upload both historical price CSV and trade CSV to begin full backtest. Use GPT and Claude summaries to archive insights or identify future entry conditions.")
