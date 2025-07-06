import streamlit as st
import openai
import pandas as pd
import altair as alt

# Load API Key (you must set in Streamlit secrets for production)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# App layout
st.set_page_config(page_title="Delta Ghost AI Options Terminal", layout="wide")

# Initialize session state
if "gpt_summary" not in st.session_state:
    st.session_state.gpt_summary = ""
if "claude_summary" not in st.session_state:
    st.session_state.claude_summary = ""
if "verdict" not in st.session_state:
    st.session_state.verdict = ""

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

# Tab: Upload CSV
if tabs == "📥 Upload CSV":
    st.title("📥 Upload Options Trade Data")
    file = st.file_uploader("Upload CSV with trade details", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df)

# Tab: P&L Heatmap
elif tabs == "📊 P&L Heatmap":
    st.title("📊 Profit & Loss Heatmap")
    file = st.file_uploader("Upload CSV with Date and P/L columns", key="pnl")
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

# Tab: GPT Summary
elif tabs == "🤖 GPT Summary":
    st.title("🤖 GPT-4 Trade Summary")
    input_text = st.text_area("Paste your trade thesis:")
    if st.button("Run GPT Summary"):
        if input_text.strip():
            result = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're a professional options analyst. Provide trade logic and tone."},
                    {"role": "user", "content": input_text}
                ]
            )
            summary = result.choices[0].message.content
            st.session_state.gpt_summary = summary
        else:
            st.warning("Please input trade thesis.")
    if st.session_state.gpt_summary:
        st.subheader("📄 GPT Output")
        st.write(st.session_state.gpt_summary)

# Tab: Claude Summary
elif tabs == "🧠 Claude Summary":
    st.title("🧠 Claude Summary Manual Entry")
    summary_text = st.text_area("Paste Claude's summary here:")
    if st.button("Save Claude Summary"):
        st.session_state.claude_summary = summary_text
    if st.session_state.claude_summary:
        st.subheader("✅ Stored Claude Summary")
        st.write(st.session_state.claude_summary)

# Tab: Compare GPT and Claude
elif tabs == "⚖️ Compare Summaries":
    st.title("⚖️ Compare GPT vs Claude")
    if st.session_state.gpt_summary and st.session_state.claude_summary:
        gpt = st.session_state.gpt_summary.lower()
        claude = st.session_state.claude_summary.lower()

        tone_gpt = "Positive" if "profit" in gpt or "upside" in gpt else "Neutral"
        tone_claude = "Positive" if "profit" in claude or "upside" in claude else "Neutral"
        st.write(f"**GPT Tone:** {tone_gpt}")
        st.write(f"**Claude Tone:** {tone_claude}")
        st.session_state.verdict = "✅ Aligned" if tone_gpt == tone_claude else "❌ Conflict"
        st.subheader("Final Verdict")
        st.success(st.session_state.verdict)
    else:
        st.warning("You need both GPT and Claude summaries first.")

# Tab: Strategy Replay
elif tabs == "📈 Strategy Replay":
    st.title("📈 Backtest / Replay Strategies")
    file = st.file_uploader("Upload batch backtest CSV", type=["csv"], key="backtest")
    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head(15))
        st.markdown("🧪 Backtest logic will be integrated here soon...")

# Tab: Sentiment Fusion
elif tabs == "⚙️ Sentiment Fusion":
    st.title("⚙️ Gemini, Reddit & Google Trends Fusion")
    g_input = st.text_area("Paste Gemini sentiment")
    r_input = st.text_area("Paste Reddit data")
    t_input = st.text_area("Paste Google Trends info")
    if st.button("Run Fusion Analysis"):
        full = f"Gemini:\n{g_input}\n\nReddit:\n{r_input}\n\nGoogle:\n{t_input}"
        result = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a market strategist analyzing sentiment for trade signal confirmation."},
                {"role": "user", "content": full}
            ]
        )
        st.subheader("🧠 Combined Summary")
        st.write(result.choices[0].message.content)
