# Stock News Digest Agent

An AI-powered agent that fetches real-time stock prices and news for a configurable watchlist, summarizes them using GPT-4o-mini, and delivers a professional HTML digest straight to your inbox via Gmail.

Built with [LangGraph](https://github.com/langchain-ai/langgraph) to orchestrate a multi-step agentic pipeline.

## How It Works

The agent runs a 5-node LangGraph pipeline:

```
Load Watchlist → Fetch Prices & News → Summarize per Stock → Compile HTML Digest → Send Email
```

1. **Load Stocks** - Reads your stock watchlist from `config/stock.yaml`
2. **Fetch News** - Pulls latest price data and news articles for each ticker via [yfinance](https://github.com/ranaroussi/yfinance)
3. **Summarize** - Uses GPT-4o-mini to generate concise bullet-point summaries with sentiment analysis (bullish/bearish/neutral)
4. **Compile Digest** - Formats all summaries into a professional HTML email with market mood, source links, and disclaimer
5. **Send Email** - Delivers the digest via Gmail API (OAuth2)

## Project Structure

```
├── main.py                  # Entry point
├── agent/
│   ├── graph.py             # LangGraph pipeline definition
│   ├── nodes.py             # Pipeline node implementations
│   ├── state.py             # State schema (TypedDict)
│   └── tools.py             # yfinance tools (price & news fetching)
├── config/
│   ├── settings.py          # Environment config (Pydantic)
│   └── stock.yaml           # Stock watchlist
├── services/
│   └── email_service.py     # Gmail OAuth2 authentication & sending
├── Dockerfile               # Container support
├── requirements.txt
└── .gitignore
```

## Prerequisites

- Python 3.13+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- Gmail API credentials (OAuth2) — follow the [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python) to get `credentials.json`

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/mohitsharma-23/Stock-Email-Project.git
   cd Stock-Email-Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** - Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GMAIL_SENDER=your_email@gmail.com
   GMAIL_RECIPIENT=recipient_email@gmail.com
   ```

4. **Add Gmail credentials** - Place your `credentials.json` file in the `services/` directory.

5. **Customize your watchlist** - Edit `config/stock.yaml`:
   ```yaml
   watchlist:
     - ticker: AAPL
       name: Apple Inc.
     - ticker: MU
       name: Micron Technology
     - ticker: TTWO
       name: Take-Two Interactive
   ```

## Usage

```bash
python main.py
```

On first run, a browser window will open for Gmail OAuth authorization. A token is saved locally so subsequent runs authenticate automatically.

### Docker

```bash
docker build -t stock-email-agent .
docker run --env-file .env stock-email-agent
```

## Sample Output

The email digest includes:
- Date and overall market mood
- Per-stock sections with current price, day change %, and summarized news bullets
- Sentiment indicator (bullish / bearish / neutral) per stock
- Source links to original articles
- Professional formatting with a disclaimer footer

## Tech Stack

- **LangGraph** - Agent orchestration
- **LangChain + OpenAI (GPT-4o-mini)** - News summarization & digest compilation
- **yfinance** - Real-time stock data & news
- **Gmail API** - Email delivery via OAuth2
- **Pydantic Settings** - Environment configuration
