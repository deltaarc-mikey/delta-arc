import streamlit as st
import pandas as pd
import openai

# App Title
st.title("📘 Strategy Replay Mode + Batch Backtest Loop")

# File Uploads
st.header("📅 Upload Historical Price Data (CSV)")
price_file = st.file_uploader("Upload your historical CSV", type=["csv"], key="price")

st.header("📈 Upload Trade History (CSV)")
trade_file = st.file_uploader("Upload your trades CSV", type=["csv"], key="trades")

# Read CSV files
if price_file:
    try:
        price_df = pd.read_csv(price_file)
        st.success("✅ Price data uploaded successfully.")
        st.dataframe(price_df.head())
    except Exception as e:
        st.error(f"❌ Failed to read price data CSV: {e}")

if trade_file:
    try:
        trade_df = pd.read_csv(trade_file)
        st.success("✅ Trade history uploaded successfully.")
        st.dataframe(trade_df.head())
    except Exception as e:
        st.error(f"❌ Failed to read trade CSV: {e}")

# GPT-4 Summary Input
st.header("🧠 Generate GPT-4 Summary")
gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=180)
run_gpt = st.button("Run GPT-4 Summary")

gpt_summary = ""
if run_gpt and gpt_input:
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Summarize the trade batch insightfully and concisely."},
                {"role": "user", "content": gpt_input}
            ]
        )
        gpt_summary = response['choices'][0]['message']['content'].strip()
        st.subheader("📄 GPT-4 Summary:")
        st.markdown(gpt_summary)
    except Exception as e:
        st.error(f"❌ GPT-4 summary generation failed: {e}")

# Claude Summary Manual Paste
st.header("📝 Claude Summary (Paste)")
claude_input = st.text_area("Paste Claude Summary", height=120)
run_claude = st.button("Run Claude Summary")

# GPT vs Claude Comparison
if (gpt_summary or gpt_input) and (claude_input or run_claude):
    gpt_comp = gpt_summary if gpt_summary else gpt_input
    st.subheader("📊 Claude vs GPT Summary Comparison")

    # Side-by-side logic (basic text match and overlap)
    st.markdown("🗂️ **Summary Comparison**")
    st.markdown("**Claude Summary:**")
    st.markdown(claude_input)

    st.markdown("**GPT Summary:**")
    st.markdown(gpt_comp)

    verdict = ""
    if claude_input and gpt_comp:
        if "profit" in claude_input.lower() and "profit" in gpt_comp.lower():
            verdict = "🟢 Both summaries indicate success. Strategy logic validated."
        elif "exit" in claude_input.lower() and "entry" in gpt_comp.lower():
            verdict = "🟡 Partial alignment — double check entry/exit logic."
        else:
            verdict = "🔴 Divergence in analysis. Reevaluate trade thesis or execution timing."

    if verdict:
        st.subheader("📌 Verdict")
        st.markdown(verdict)

# Final reminder
st.info("📘 Upload both historical price CSV and trade CSV to begin full backtest. Use GPT and Claude summaries to archive insights or identify future entry conditions.")
