import os
import openai
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- GPT Trade Summary Processor ----------
def process_gpt_summary(summary_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional options trader and financial analyst."},
                {"role": "user", "content": f"""
The following is a trade setup summary. Return:
1. Your confidence score from 1 to 100 (as a number only),
2. The tone (positive, neutral, or negative),
in JSON format with keys: confidence and tone.

Text:
\"\"\"
{summary_text}
\"\"\"
                """}
            ],
            temperature=0.5
        )
        reply = response.choices[0].message.content.strip()
        return reply
    except Exception as e:
        return f"Error: {e}"

# ---------- Layout ----------
st.set_page_config(page_title="Delta Ghost – Trade Validator", layout="wide")
st.title("📉 Delta Ghost – Trade Validator")

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["📊 Trade Validator", "⚡ Claude Prompt Tuner"])

# ---------- Tab 1: Trade Validator ----------
with tab1:
    st.subheader("📌 Trade Evaluation Results")

    gpt_input = st.text_area("🧠 GPT Summary Prompt Input", height=180, placeholder="Paste GPT trade summary here...")
    claude_input = st.text_area("🧠 Claude Summary Text (Paste manually)", height=160, placeholder="Paste Claude analysis here...")

    if st.button("▶️ Run GPT Summary"):
        if gpt_input.strip() == "":
            st.warning("Please enter a GPT trade summary.")
        else:
            result = process_gpt_summary(gpt_input)
            try:
                parsed = eval(result) if isinstance(result, str) else result
                gpt_confidence = parsed.get("confidence", "N/A")
                gpt_tone = parsed.get("tone", "N/A")
            except:
                gpt_confidence = "ParseError"
                gpt_tone = "ParseError"

            # Estimate Claude tone manually
            if "bullish" in claude_input.lower():
                claude_tone = "Positive"
            elif "cautious" in claude_input.lower():
                claude_tone = "Neutral"
            elif "bearish" in claude_input.lower():
                claude_tone = "Negative"
            else:
                claude_tone = "N/A"

            # Auto Score Logic
            try:
                auto_score = int(gpt_confidence) if gpt_confidence != "ParseError" else 0
            except:
                auto_score = 0

            st.markdown("### 📈 Trade Summary Evaluation Table")
            df = pd.DataFrame([{
                "Ticker": "Manual Input",
                "GPT Confidence Score": gpt_confidence,
                "GPT Tone": gpt_tone,
                "Claude Tone": claude_tone,
                "Auto Score": auto_score
            }])
            st.dataframe(df, use_container_width=True)

# ---------- Tab 2: Claude Prompt Tuner ----------
with tab2:
    st.subheader("🛠 Claude Prompt Tuner")
    st.markdown("""
Use this section to refine prompt instructions you’ll copy/paste into Claude manually.

**Template:**
