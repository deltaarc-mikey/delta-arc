import streamlit as st
import openai
import pandas as pd
import altair as alt

# Set Streamlit layout
st.set_page_config(page_title="Delta Ghost AI Trading Terminal", layout="wide")

# Load OpenAI key from secrets (REQUIRED on Streamlit Cloud)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Session state setup
for key in ["gpt_summary", "claude_summary", "verdict"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# Sidebar navigation
tabs = st.sidebar.radio("Navigate", [
    "📥 Upload CSV",
    "📊 P&L Heatmap",
    "🤖 GPT Summary",
    "🧠 Claude Summary",
    "⚖️ Compare Summaries",
    "📈 Strategy Replay",
    "⚙️ Sentiment Fusion"
])

# Upload CSV Tab
if tabs == "📥 Upload CSV":
    st.title("📥 Upload Options Trade Data")
    file = st.file_uploader("Upload CSV with trade details", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df)

# P&L Heatmap Tab
elif tabs == "📊 P&L Heatmap":
    st.title("📊 Profit & Loss Heatmap")
    file = st.file_uploader("Upload CSV with Date and P/L columns", key="pnl_upload")
    if file:
        df = pd.read_csv(file)
        if "Date" in df.columns and "P/L" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            chart = alt.Chart(df).mark_rect().encode(
                x='month(Date):O',
                y='day(Date):O',
                color='mean(P/L):Q'
            ).properties(width=600, height=300)
            st.altair_chart(chart)
        else:
            st.error("CSV must contain 'Date' and 'P/L' columns.")

# GPT Summary Tab
elif tabs == "🤖 GPT Summary":
    st.title("🤖 GPT-4 Trade Summary")
    input_text = st.text_area("Paste your trade thesis:")
    if st.button("Run GPT Summary"):
        if input_text.strip():
            try:
                result = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You're a professional options analyst. Provide trade logic and tone."},
                        {"role": "user", "content": input_text}
                    ]
                )
                summary = result.choices[0].message.content
                st.session_state.gpt_summary = summary
                st.success("✅ GPT Summary generated.")
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")
        else:
            st.warning("Please input trade thesis.")
    if st.session_state.gpt_summary:
        st.subheader("📄 GPT Output")
        st.write(st.session_state.gpt_summary)

# Claude Summary Tab
elif tabs == "🧠 Claude Summary":
    st.title("🧠 Claude Summary Manual Entry")
    summary_text = st.text_area("Paste Claude's summary here:")
    if st.button("Save Claude Summary"):
        st.session_state.claude_summary = summary_text
        st.success("✅ Claude Summary saved.")
    if st.session_state.claude_summary:
        st.subheader("📄 Stored Claude Summary")
        st.write(st.session_state.claude_summary)

# Comparison Tab
elif tabs == "⚖️ Compare Summaries":
    st.title("⚖️ GPT vs Claude Summary Comparison")
    if st.session_state.gpt_summary and st.session_state.claude_summary:
        gpt = st.session_state.gpt_summary.lower()
        claude = st.session_state.claude_summary.lower()

        tone_gpt = "Positive" if any(w in gpt for w in ["profit", "upside", "gain"]) else "Neutral"
        tone_claude = "Positive" if any(w in claude for w in ["profit", "upside", "gain"]) else "Neutral"
        
        st.write(f"**GPT Tone:** {tone_gpt}")
        st.write(f"**Claude Tone:** {tone_claude}")
        
        aligned = tone_gpt == tone_claude
        verdict = "✅ Aligned" if aligned else "❌ Mismatch"
        st.session_state.verdict = verdict
        st.subheader("🧠 Verdict")
        st.success(verdict) if aligned else st.error(verdict)
    else:
        st.warning("Please generate GPT and paste Claude summary first.")

# Strategy Replay Tab
elif tabs == "📈 Strategy Replay":
    st.title("📈 Strategy Replay Upload")
    file = st.file_uploader("Upload historical trade strategy CSV", key="replay_csv")
    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head())
        st.info("💡 Backtest logic to be integrated here.")

# Sentiment Fusion Tab
elif tabs == "⚙️ Sentiment Fusion":
    st.title("⚙️ Gemini, Reddit, and Google Trends Sentiment Fusion")
    g_input = st.text_area("🔮 Paste Gemini output:")
    r_input = st.text_area("🧠 Paste Reddit signal:")
    t_input = st.text_area("📈 Paste Google Trends insight:")
    if st.button("Run Sentiment Fusion"):
        if any([g_input, r_input, t_input]):
            full_prompt = f"Gemini:\n{g_input}\n\nReddit:\n{r_input}\n\nGoogle:\n{t_input}"
            try:
                result = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a financial analyst combining sentiment sources to decide if a trade thesis is valid or risky."},
                        {"role": "user", "content": full_prompt}
                    ]
                )
                st.subheader("📊 Fusion Summary")
                st.write(result.choices[0].message.content)
            except Exception as e:
                st.error(f"❌ GPT Error: {e}")
        else:
            st.warning("Please input at least one sentiment source.")
