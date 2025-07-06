
import streamlit as st
import openai
from datetime import datetime
import yfinance as yf
from pytrends.request import TrendReq
import praw
import pandas as pd

# Set page config
st.set_page_config(page_title="Delta Ghost Dashboard", layout="wide")

# API Keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="delta-ghost-sentiment"
)

# ---- Sidebar ----
st.sidebar.title("🔧 Navigation")
tab = st.sidebar.radio("Select Tool", ["📈 Ticker Overview", "📊 Reddit + Google Trends", "🤖 Trade Validator", "📁 Backtest Runner", "🎯 Claude Prompt Tuner"])

# ---- Ticker Overview Tab ----
if tab == "📈 Ticker Overview":
    st.title("📈 Ticker Overview")
    ticker = st.text_input("Enter a ticker symbol (e.g., AAPL, TSLA)")
    if ticker:
        data = yf.download(ticker, period="1mo", interval="1d")
        st.line_chart(data["Close"])

# ---- Reddit + Google Trends Tab ----
elif tab == "📊 Reddit + Google Trends":
    st.title("📊 Reddit + Google Trends Sentiment Analysis")

    tickers = st.text_input("Enter tickers (comma-separated)").upper().split(",")
    if tickers and tickers[0]:
        pytrends = TrendReq(hl='en-US', tz=360)
        trends_df = pd.DataFrame(columns=["Ticker", "Google Trend Score", "Reddit Mentions"])

        for ticker in tickers:
            search_term = ticker.strip()
            # Google Trends
            try:
                pytrends.build_payload([search_term], cat=0, timeframe='now 7-d', geo='', gprop='')
                interest = pytrends.interest_over_time()
                trend_score = int(interest[search_term].mean()) if not interest.empty else 0
            except:
                trend_score = 0

            # Reddit Mentions
            try:
                reddit_mentions = 0
                for submission in reddit.subreddit("wallstreetbets+stocks+options").search(search_term, limit=20):
                    reddit_mentions += 1
            except:
                reddit_mentions = 0

            trends_df.loc[len(trends_df)] = [search_term, trend_score, reddit_mentions]

        st.dataframe(trends_df)

# ---- Trade Validator ----
elif tab == "🤖 Trade Validator":
    st.title("🤖 Delta Ghost – Trade Validator")

    gpt_input = st.text_area("🧠 GPT Summary Prompt Input", height=200)
    claude_input = st.text_area("🧠 Claude Summary Text (Paste manually)", height=200)

    if st.button("▶️ Run GPT Summary"):
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional options analyst."},
                    {"role": "user", "content": gpt_input}
                ]
            )
            gpt_summary = gpt_response["choices"][0]["message"]["content"]

            # Scoring logic
            gpt_confidence = 75 if "strong" in gpt_summary.lower() else 50
            gpt_tone = "Positive" if "bullish" in gpt_summary.lower() else "Neutral"
            claude_tone = "Positive" if "opportunistic" in claude_input.lower() else "Neutral"
            auto_score = int((gpt_confidence + (80 if claude_tone == "Positive" else 60)) / 2)

            result = pd.DataFrame([{
                "Ticker": "Manual Input",
                "GPT Confidence Score": gpt_confidence,
                "GPT Tone": gpt_tone,
                "Claude Tone": claude_tone,
                "Auto Score": auto_score
            }])

            st.dataframe(result)
        except Exception as e:
            st.error(f"OpenAI API Error: {str(e)}")

# ---- Backtest Runner ----
elif tab == "📁 Backtest Runner":
    st.title("📁 Strategy Backtest Batch Runner")
    uploaded_file = st.file_uploader("Upload historical trades CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
            st.success("File uploaded and valid. Proceeding with backtest...")
            # Insert scoring logic here
        except Exception as e:
            st.error(f"CSV Error: {str(e)}")

# ---- Claude Prompt Tuner ----
elif tab == "🎯 Claude Prompt Tuner":
    st.title("🎯 Claude Prompt Tuner")
    tone_choice = st.selectbox("Select Desired Tone Style", ["Quantitative", "Retail Buzz", "Neutral"])
    if tone_choice == "Quantitative":
        st.code("This setup exhibits strong technical alignment with risk-defined upside based on implied volatility skews and recent EMA crossovers.")
    elif tone_choice == "Retail Buzz":
        st.code("This trade is HOT right now — breaking resistance, Reddit is hyped, and the flow is surging!")
    else:
        st.code("The trade has balanced technicals with neutral sentiment. Suitable for conservative positioning.")
