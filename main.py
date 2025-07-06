import streamlit as st
import pandas as pd
import base64


# ----- Reddit Sentiment Script Logic -----
def run_reddit_sentiment():
    import praw
    import pandas as pd
    from datetime import datetime
    import os

    # Placeholder credentials - replace with your actual values or secrets
    reddit = praw.Reddit(
        client_id='YOUR_CLIENT_ID',
        client_secret='YOUR_CLIENT_SECRET',
        user_agent='delta-ghost-ai-sentiment'
    )

    subreddits = ['options', 'stocks', 'wallstreetbets', 'Daytrading']
    keywords = ['call', 'put', 'bullish', 'bearish']
    posts = []

    for sub in subreddits:
        for post in reddit.subreddit(sub).hot(limit=50):
            if any(word in post.title.lower() for word in keywords):
                posts.append({
                    'subreddit': sub,
                    'title': post.title,
                    'score': post.score,
                    'created': datetime.fromtimestamp(post.created_utc),
                    'url': post.url
                })

    df = pd.DataFrame(posts)
    filename = f'reddit_sentiment_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
    filepath = os.path.join('./data', filename)
    df.to_csv(filepath, index=False)
    return filepath


# ----- Unusual Whales Real API Fetch Logic -----
    import pandas as pd
    from datetime import datetime
    import os

def run_unusual_whales():
    import requests
    import pandas as pd
    from datetime import datetime
    import os

    UW_API_KEY = os.getenv("UW_API_KEY")  # Store securely via environment or secrets manager
    headers = {"Authorization": f"Bearer {UW_API_KEY}"}

    # Define query parameters
    endpoint = "https://api.unusualwhales.com/api/historic_chains"
    params = {
        "limit": 100,
        "min_premium": 0.01,
        "max_premium": 0.50,
        "earliest_expiration": "2025-11-17",
        "type": "all",
        "sort": "volume",
        "order": "desc"
    }

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("chains", [])

        df = pd.DataFrame(data)
        if df.empty:
            raise ValueError("No data returned from UW API.")

        df = df[df['ask'] <= 0.50]
        df = df[df['expiration'] >= "2025-11-17"]
        df = df[df['open_interest'] > 1000]

        filename = f"uw_live_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
        filepath = os.path.join("./data", filename)
        df.to_csv(filepath, index=False)
        return filepath

    except Exception as e:
        return f"❌ Error pulling UW data: {str(e)}"
    sample_data = {
        'ticker': ['TSLA', 'AAPL', 'NVDA'],
        'strike': [250, 200, 130],
        'expiry': ['2025-11-21', '2025-11-21', '2025-11-21'],
        'type': ['Call', 'Call', 'Put'],
        'cost': [0.45, 0.38, 0.50],
        'volume': [12000, 15000, 9800]
    }

    df = pd.DataFrame(sample_data)
    filename = f'unusual_whales_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
    filepath = os.path.join('./data', filename)
    df.to_csv(filepath, index=False)
    return filepath


st.set_page_config(page_title="Delta Ghost: Options AI", layout="wide")
st.title("📈 Delta Ghost: AI-Powered Options Intelligence")

# Sidebar
st.sidebar.header("📂 Upload & Filter")
uploaded_file = st.sidebar.file_uploader("Upload CSV with Options Data", type=["csv"])

cost_limit = st.sidebar.number_input("Max Cost per Contract ($)", min_value=0.0, value=0.50, step=0.05)

# Tabs setup
tabs = st.tabs(["📊 Summary", "🤖 LLM Output", "🔍 Unusual Options Activity", "📢 Reddit Sentiment", "📈 Google Trends", "🕹️ Morning Checklist"])

# Placeholder for data
options_df = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        options_df = df[df["price"] <= cost_limit]
    except Exception as e:
        st.sidebar.error(f"Failed to process file: {e}")

# Summary Tab
with tabs[0]:
    st.subheader("📊 Summary of Filtered Contracts")
    if options_df is not None:
        st.write(f"Showing {len(options_df)} contracts under ${cost_limit:.2f} per contract")
        st.dataframe(options_df, use_container_width=True)
    else:
        st.info("Upload a CSV to see summary data.")

# LLM Output Tab (Claude/GPT manual ingestion)
with tabs[1]:
    st.subheader("🤖 Paste LLM Output (Claude or GPT)")
    llm_text = st.text_area("Paste full LLM output text here:")
    if llm_text:
        st.markdown("### Parsed Output")
        st.write(llm_text)

# Unusual Options Activity Tab
with tabs[2]:
    st.subheader("🔍 Unusual Options Activity Summary")
    uoa_notes = st.text_area("Paste UOA comments or summarized signals here:")
    if uoa_notes:
        st.markdown("### UOA Commentary")
        st.write(uoa_notes)

# Reddit Sentiment Tab
with tabs[3]:
    st.subheader("📢 Reddit Sentiment Scan")
    reddit_text = st.text_area("Paste Reddit sentiment summary or findings here:")
    if reddit_text:
        st.markdown("### Reddit Market Pulse")
        st.write(reddit_text)

# Google Trends Tab
with tabs[4]:
    st.subheader("📈 Google Trends Snapshot")
    trends_text = st.text_area("Paste Google Trends summary or screenshot notes here:")
    if trends_text:
        st.markdown("### Trend Commentary")
        st.write(trends_text)

# Footer
st.markdown("---")
st.caption("Developed by Delta Ghost | AI-driven Options Strategy | Version 2.0")



# Morning Checklist Tab
with tabs[5]:
    st.subheader("🕹️ Delta Ghost — Morning Trade Checklist")

    if 'checklist' not in st.session_state:
        st.session_state['checklist'] = {
            'devices_ready': False,
            'logged_in': False,
            'uw_data': False,
            'xynth': False,
            'finviz': False,
            'reddit': False,
            'trends': False,
            'prompt_gpt': False,
            'prompt_gemini': False,
            'review_final': False,
            'trade_execution': False,
            'trade_logged': False,
        }

    def checklist_step(key, label):
        st.session_state['checklist'][key] = st.checkbox(label, value=st.session_state['checklist'][key])

    st.subheader("🔧 1. System Setup")
    checklist_step('devices_ready', "Boot devices (Laptop, Phone, Power)")
    checklist_step('logged_in', "Log in to TastyTrade, Robinhood, Zapier, Drive")

    st.subheader("📥 2. Ingest Data")
    col1, col2 = st.columns(2)
    with col1:
        checklist_step('uw_data', "Pull Unusual Whales data")
        if st.button("▶ Run UW Script"):
            st.success("✅ UW Data Pull Triggered (Simulated Call to UW Tab Logic)")
            # Place actual function call here if modularized: run_unusual_whales()
        checklist_step('xynth', "Run/download Xynth Momentum Report")
    with col2:
        checklist_step('reddit', "Run Reddit Sentiment script")
        if st.button("▶ Run Reddit Script"):
            st.success("✅ Reddit Sentiment Triggered (Simulated Call to Reddit Tab Logic)")
            # Place actual function call here if modularized: run_reddit_sentiment()
        checklist_step('finviz', "Scan Finviz Screener (manual)")
        checklist_step('trends', "Check Google Trends (manual or PyTrends)")

    st.subheader("🧠 3. AI Analysis")
    checklist_step('prompt_gpt', "Prompt GPT-4o for trade recommendations")
    checklist_step('prompt_gemini', "Prompt Gemini via Vertex AI")

    st.subheader("📄 4. Final Review")
    checklist_step('review_final', "Ingest LLM outputs and finalize strategy")

    st.subheader("🚀 5. Execute Trades")
    checklist_step('trade_execution', "Manually enter trades into broker")
    checklist_step('trade_logged', "Log trade in Google Form/Sheet")

    st.markdown("---")
    st.subheader("📊 Summary")
    completed = sum(v for v in st.session_state['checklist'].values())
    total = len(st.session_state['checklist'])
    st.success(f"{completed} of {total} steps completed")

    if st.button("🔄 Reset Checklist"):
        for k in st.session_state['checklist']:
            st.session_state['checklist'][k] = False
        st.experimental_rerun()
