# Claude Summary Support Integration (for GPT & Claude Comparison)
# Adds the logic to display Claude's manual summary alongside GPT output in UI.

import streamlit as st
import pandas as pd
import openai
import os

# --- Claude + GPT Summary Section ---
st.header("🤖 Claude + GPT Trade Summary Viewer")

# Upload Claude summary manually (from .txt or .docx)
claude_summary_file = st.file_uploader("📥 Upload Claude Summary (.txt or .docx)", type=["txt", "docx"])
claude_summary = ""

if claude_summary_file:
    if claude_summary_file.name.endswith(".txt"):
        claude_summary = claude_summary_file.read().decode("utf-8")
    elif claude_summary_file.name.endswith(".docx"):
        from docx import Document
        doc = Document(claude_summary_file)
        claude_summary = "\n".join([para.text for para in doc.paragraphs])

# GPT summarization of trades
gpt_summary = ""
if 'trades_df' in st.session_state:
    trade_df = st.session_state['trades_df']
    trade_rows = trade_df.to_dict(orient="records")
    gpt_input = "".join([f"Trade {i+1}: {row}\n" for i, row in enumerate(trade_rows)])

    if st.button("Run GPT-4 Summary"):
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            chat_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional trading analyst. Summarize the trades logically and evaluate strengths/weaknesses."},
                    {"role": "user", "content": gpt_input}
                ]
            )
            gpt_summary = chat_response['choices'][0]['message']['content']
        except Exception as e:
            st.error(f"Error from GPT-4: {e}")

# Display Results
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Claude Summary")
    if claude_summary:
        st.text_area("Claude Summary Output", value=claude_summary, height=300)
    else:
        st.info("Please upload a Claude-generated summary file.")

with col2:
    st.subheader("🧠 GPT-4 Summary")
    if gpt_summary:
        st.text_area("GPT Summary Output", value=gpt_summary, height=300)
    else:
        st.info("Press 'Run GPT-4 Summary' after uploading a trade CSV.")
