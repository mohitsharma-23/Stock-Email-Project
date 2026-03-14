# Stock News Digest Agent

An AI-powered agent that fetches real-time stock prices and news for a configurable watchlist, summarizes them using GPT-4o-mini, and delivers a professional HTML digest straight to your inbox via Gmail.

Built with [LangGraph](https://github.com/langchain-ai/langgraph) to orchestrate a multi-step agentic pipeline.

## What it does

There are 5 steps that run in sequence:

```
Load watchlist -> Fetch prices & news -> Summarize -> Build HTML email -> Send via Gmail
```

- Reads tickers from a YAML config file
- Grabs real-time prices and recent headlines using [yfinance](https://github.com/ranaroussi/yfinance)
- Summarizes each stock into bullet points with sentiment (bullish/bearish/neutral)
- Compiles everything into a styled HTML email
- Sends it through Gmail API (OAuth2)

## Project structure

```
├── main.py                  # entry point
├── agent/
│   ├── graph.py             # LangGraph pipeline
│   ├── nodes.py             # each step in the pipeline
│   ├── state.py             # state schema
│   └── tools.py             # yfinance wrappers
├── config/
│   ├── settings.py          # env config (pydantic)
│   └── stock.yaml           # watchlist
├── services/
│   └── email_service.py     # Gmail OAuth + sending
├── Dockerfile
├── requirements.txt
└── .gitignore
```

## Getting started

You'll need:
- Python 3.13+
- An OpenAI API key
- Gmail API OAuth credentials (`credentials.json`). See the [Gmail quickstart guide](https://developers.google.com/gmail/api/quickstart/python)

### Setup

```bash
git clone https://github.com/mohitsharma-23/Stock-Email-Project.git
cd Stock-Email-Project
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=your_key_here
GMAIL_SENDER=you@gmail.com
GMAIL_RECIPIENT=whoever@gmail.com
```

Drop your `credentials.json` into the `services/` folder.

### Configure your watchlist

Edit `config/stock.yaml` to add/remove stocks:

```yaml
watchlist:
  - ticker: AAPL
    name: Apple Inc.
  - ticker: MU
    name: Micron Technology
  - ticker: TTWO
    name: Take-Two Interactive
```

### Run it

```bash
python main.py
```

First time it'll open a browser for Gmail auth. After that it saves a token locally so you won't need to do it again.

### Docker

```bash
docker build -t stock-email-agent .
docker run --env-file .env stock-email-agent
```

## What the email looks like

Each digest has:
- Today's date + a one-line market mood summary
- Per-stock section with price, day change, and news bullets
- Sentiment tag per stock
- Links to the original articles
- Disclaimer at the bottom

## Built with

LangGraph, LangChain, OpenAI (GPT-4o-mini), yfinance, Gmail API, Pydantic
