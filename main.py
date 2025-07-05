
import streamlit as st
import pandas as pd
import openai
from docx import Document
import base64

# --- Page Config ---
st.set_page_config(page_title="Claude vs GPT Summary Comparison", layout="wide")

# --- API Key Setup ---
openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# --- Helper: Read Claude File ---
def read_uploaded_file(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file type."

# --- Claude vs GPT Comparison UI ---
st.title("🤖 Claude vs GPT Summary Comparison")
st.markdown("Upload your Claude-generated summary and compare it with a GPT-4 summary in real-time.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Upload Claude Summary (.txt or .docx)")
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx"], key="claude_file")
    claude_text = ""
    if uploaded_file:
        claude_text = read_uploaded_file(uploaded_file)
        st.text_area("Claude Summary Content", value=claude_text, height=300)

with col2:
    st.subheader("✍️ Generate GPT-4 Summary")
    gpt_input = st.text_area("Paste input for GPT-4 summary (e.g. trade batch details)", height=300)
    if st.button("Run GPT-4 Summary"):
        if gpt_input and openai.api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a professional financial analyst. Summarize this batch of trade results clearly."},
                        {"role": "user", "content": gpt_input}
                    ]
                )
                gpt_output = response['choices'][0]['message']['content']
                st.text_area("GPT-4 Summary Output", value=gpt_output, height=300)
            except Exception as e:
                st.error(f"Error generating GPT summary: {e}")
        else:
            st.warning("Please provide GPT input and ensure API key is set.")

# --- Comparison Side-by-Side ---
if claude_text and gpt_input:
    st.markdown("### 🧠 Claude vs GPT Side-by-Side Comparison")
    col1, col2 = st.columns(2)
    col1.markdown("#### Claude Summary")
    col1.write(claude_text)
    col2.markdown("#### GPT-4 Summary")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Summarize this text:"},
                {"role": "user", "content": gpt_input}
            ]
        )
        col2.write(response['choices'][0]['message']['content'])
    except Exception as e:
        col2.error(f"Error displaying GPT summary: {e}")
