# -*- coding: utf-8 -*-
import os
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import streamlit as st
import io
import contextlib

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain import hub

# ---- TOOL DEFINITIONS ----
def get_stock_data(ticker_symbol):
    """Fetches recent stock price data."""
    stock_data = yf.download(ticker_symbol, period='10d', progress=False)
    return stock_data.to_string()

def get_manual_options_data(ticker_symbol):
    """Reads manually uploaded options data from a file."""
    try:
        with open('options_data.txt', 'r') as f:
            full_text = f.read()
        sections = full_text.split('---')
        for section in sections:
            if f"TICKER: {ticker_symbol.upper()}" in section:
                return section.strip()
        return f"No options data found for {ticker_symbol} in the file."
    except FileNotFoundError:
        return "The 'options_data.txt' file was not found. Please upload it to the GitHub repository."

def get_fundamental_data(ticker_symbol):
    """Gets key fundamental data by directly scraping the Finviz website."""
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker_symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        snapshot_table = soup.find('table', class_='snapshot-table2')
        data = {}
        rows = snapshot_table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            for i in range(0, len(cols), 2):
                metric = cols[i].text.strip()
                value = cols[i+1].text.strip()
                data[metric] = value
        key_metrics = {"Market Cap": data.get("Market Cap"), "P/E": data.get("P/E"), "EPS (ttm)": data.get("EPS (ttm)")}
        return "\n".join([f"{key}: {value}" for key, value in key_metrics.items()])
    except Exception as e:
        return f"Could not retrieve Finviz data for {ticker_symbol}. Error: {e}"

def run_full_analysis(ticker_symbol):
    """Runs a full analysis by gathering all available data."""
    price_data = get_stock_data(ticker_symbol)
    fundamental_data = get_fundamental_data(ticker_symbol)
    options_data = get_manual_options_data(ticker_symbol)
    return f"ANALYSIS FOR {ticker_symbol}:\n\nPrice Data:\n{price_data}\n\nFundamental Data:\n{fundamental_data}\n\nManual Options Data:\n{options_data}"

# ---- AGENT AND UI SETUP ----
st.title("🤖 AI Financial Analyst")

if 'agent_executor' not in st.session_state:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=st.secrets["secret"])
    tools = [
        Tool(name="run_full_analysis", func=run_full_analysis, description="Use when the user asks for a 'full analysis', 'summary', or 'overview'. Gathers all info."),
        Tool(name="get_stock_data", func=get_stock_data, description="Use for recent stock market PRICE and VOLUME data."),
        Tool(name="get_manual_options_data", func=get_manual_options_data, description="Use for manually uploaded OPTIONS FLOW data."),
        Tool(name="get_fundamental_data", func=get_fundamental_data, description="Use for key FUNDAMENTAL metrics (P/E, Market Cap, etc.).")
    ]
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    st.session_state.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

user_question = st.text_input("Ask a question (e.g., 'Give me a full analysis of NVDA'):")

if user_question:
    string_io = io.StringIO()
    with st.spinner("Thinking..."):
        with contextlib.redirect_stdout(string_io):
            response = st.session_state.agent_executor.invoke({"input": user_question})
        thought_process = string_io.getvalue()

    st.markdown("### Final Answer:")
    st.write(response.get("output"))

    with st.expander("Show Thought Process"):
        st.text(thought_process)
