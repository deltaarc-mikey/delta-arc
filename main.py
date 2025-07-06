import streamlit as st
import pandas as pd
import openai
import requests
import datetime
from textblob import TextBlob
import tweepy

# Twitter API setup (REPLACE with your credentials)
twitter_bearer_token = "YOUR_TWITTER_BEARER_TOKEN"
client = tweepy.Client(bearer_token=twitter_bearer_token)

def fetch_twitter_sentiment(ticker):
    try:
        query = f"${ticker} stock -is:retweet lang:en"
        tweets = client.search_recent_tweets(query=query, max_results=20, tweet_fields=['text'])
        tweet_texts = [tweet.text for tweet in tweets.data] if tweets.data else []
        sentiments = [TextBlob(text).sentiment.polarity for text in tweet_texts]
        avg_sentiment = round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.0
        return avg_sentiment, tweet_texts
    except Exception as e:
        return 0.0, [f"Error: {e}"]

def auto_score_trade(row):
    base_score = row.get('GPT Confidence Score', 0)
    gpt_tone = row.get('GPT Tone', '').lower()
    claude_tone = row.get('Claude Tone', '').lower()
    twitter_sentiment = row.get('Twitter Sentiment', 0.0)

    bonus = 0
    if gpt_tone == 'positive':
        bonus += 5
    if claude_tone == 'positive':
        bonus += 5
    if twitter_sentiment > 0.2:
        bonus += 5
    
    return min(base_score + bonus, 100)

# Streamlit UI
st.set_page_config(page_title="Delta Ghost Trading AI Suite", layout="wide")
st.title("🧠 Delta Ghost AI Trade Validator + Twitter/X Integrator")

uploaded_file = st.file_uploader("📥 Upload your options trades CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'Ticker' not in df.columns:
        st.error("❌ CSV must include a 'Ticker' column.")
    else:
        st.success("✅ File uploaded and valid. Proceeding...")

        twitter_sentiments = []
        twitter_notes = []

        with st.spinner("🔍 Fetching Twitter sentiment..."):
            for idx, row in df.iterrows():
                sentiment_score, notes = fetch_twitter_sentiment(row['Ticker'])
                twitter_sentiments.append(sentiment_score)
                twitter_notes.append("\n".join(notes[:3]))

        df['Twitter Sentiment'] = twitter_sentiments
        df['Twitter Notes'] = twitter_notes
        df['Auto Score'] = df.apply(auto_score_trade, axis=1)

        st.markdown("### 🔎 Twitter Sentiment Analysis")
        st.dataframe(df[['Ticker', 'Twitter Sentiment', 'Twitter Notes']])

        st.markdown("### 📊 Trade Scoring (GPT + Claude + Twitter)")
        st.dataframe(df[['Ticker', 'GPT Confidence Score', 'GPT Tone', 'Claude Tone', 'Twitter Sentiment', 'Auto Score']])

        csv_output = df.to_csv(index=False).encode('utf-8')
        st.download_button("📤 Download Updated CSV", csv_output, file_name="scored_trades.csv", mime="text/csv")

st.sidebar.title("🔧 Toolset Navigation")
st.sidebar.info("Integrated Twitter API sentiment + trade scoring engine based on GPT, Claude, and real-time Twitter mentions.")
st.sidebar.markdown("---")
st.sidebar.success("✅ Ready for backtesting or execution queue")
