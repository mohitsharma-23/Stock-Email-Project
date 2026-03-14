import yaml
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import dotenv
import os
from datetime import date

from agent.state import StockNewsState
from agent.tools import fetch_stock_price, fetch_stock_news

# Creating the nodes for the graph

#---------------------------------------------------------------------
# NODE 1: Loading the stock list
#---------------------------------------------------------------------

def load_stocks_node(state: StockNewsState) -> StockNewsState:
    """Load the stock watchlist from stocks.yaml"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "stock.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
        print(f"Loaded {len(config['watchlist'])} stocks from the stock lists.")
        return {
            "stocks": config['watchlist']
        }


#---------------------------------------------------------------------
# NODE 2: Fetching the news and the stock price for all the stocks
#---------------------------------------------------------------------
def fetch_news_node(state: StockNewsState) -> StockNewsState:
    """
    For each stock, fetch:
    - Latest news articles (via yfinance)
    - Current price and change percentage (via finance)
    """
    all_news =[]
    errors = []


    for stock in state['stocks']:
        ticker = stock['ticker']
        # Fetch the stock price for the stock
        price_info = fetch_stock_price.invoke({
            "ticker": ticker
        })

        #Fetch the news related to the stock
        stock_news = fetch_stock_news.invoke({
            "ticker": ticker
        })

        #Combining the price and the news info together
        for article in stock_news:
            if "error" not in article:
                article["price_context"] = price_info
        
        #Checking for any errors
        valid = [a for a in stock_news if "error" not in a]
        if not valid:
            errors.append(f"No valid news fetched for {ticker}")

        all_news.extend(stock_news)

    print(f"Total articles fetched: {len([a for a in all_news if 'error' not in a])}")
    # print(f"Stock News: {all_news}")
    return {
        "stock_news": all_news,
        "errors": errors
    }

#---------------------------------------------------------------------
# NODE 3: Summarize all news for each stock
#---------------------------------------------------------------------
def summarize_node(state: StockNewsState) -> StockNewsState:
    """
    For each of the stock summarize the news using LLMs
    """
    summaries = []

    #Creating the LLM client for providing the prompts
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model='gpt-4o-mini', temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [(
        "system", """You are helpful summarizing agent. Given the list of news for the stocks help to summarize the news
        - Summarize into 4-5 bullet points for each stock
        - The 1st point should always include the current stock price and the day percentage change
        - Prioritize the news containing information about the stock followed by any news which impacts the stock indirectly
        - Mention any notable risks if mentioned
        - Strictly summarize only based on the input received without any additional information
        - Provide the sentiment (bearish/bullish/neutral) in one line. Provide the sentiment based on the below rules:
            Bullish - positive news about the stock, price increase, posisitve earnings, upgrades, price aboe previous close
            Bearish - negative news about the stock, price decrease, negative earnings, downgrades, price below previous close
            Neutral - no significant news, price stable, no change in earnings, no upgrades/downgrades, mixed signals or no strong directional news.
         4. Source of each of the news.
        - Always provide the list of url of the news article for the user to refer to
        Be factual, concise and avoid any speculations.
        """
    ),(
        "human", """Stock {ticker} - {company}. 
        Current Price: {current_price} | Day Change: {day_change_pct} | Day High: {day_high} | Day Low: {day_low}.
        Recent news : {stock_news}.
        Provide your summary.
        """)
    ])

    #Create the chain for the summarizing
    summarize_chain = prompt | llm
    
    # Segregate the news for each stock based on the ticker
    news_by_ticker: dict[str, list[dict]] = {}
    for article in state["stock_news"]:
        ticker = article.get("ticker", "UNKNOWN")
        if "error" not in article:
            news_by_ticker.setdefault(ticker, []).append(article)
    
    for stock in state["stocks"]:
        ticker = stock["ticker"]
        articles = news_by_ticker.get(ticker)

        if not articles:
            print(f"No articles found for {ticker}")
            continue

        print(f"Summarizing the articles for {ticker} having {len(articles)} news.....")

        price_info = articles[0].get("price_context", {})
        article_text = "\n\n".join([
            f"[{a['title']} {a['description']} {a['url']} {a['content_type']}]" for a in articles
        ])

        response = summarize_chain.invoke(
            {
                "ticker": ticker,
                "company": stock['name'],
                "current_price": price_info['current_price'],
                "day_change_pct": price_info['day_change_pct'],
                "day_high": price_info['day_high'],
                'day_low': price_info['day_low'],
                "stock_news": article_text
            }
        )

        summaries.append({
            "ticker": ticker,
            "company": stock["name"],
            "price_context": price_info,
            "summary": response.content,
            "article_count": len(articles),
            "article_urls": [a['url'] for a in articles if a.get("url")]
        })

    return {
            "summaries": summaries
    } 

#---------------------------------------------------------------------
# NODE 4: Compile all summaries into HTML content 
#---------------------------------------------------------------------
def compile_digest_node(state: StockNewsState) -> StockNewsState:
    """Compile all per-stock summaries into a single formatted HTML email body"""
    dotenv.load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model='gpt-4o-mini', temperature=0, model_kwargs={"seed":42})

    digest_prompt = ChatPromptTemplate.from_messages([
        ('system', """You are a financial newletter editor.
         Create a professional daily stock digest news formatted as clean, readable HTML email.
         Structure:
         1. Header with today's date {date} and a one-line overall market mood sentence based on the summaries.
         2. One section per stock with price and bullet points about the stock news.
         3. Each stock should show the sentiment based on the news about the stock (bearish/ bullish/ neutral). Provide the sentiment based on the below rules:
            Bullish - positive news about the stock, price increase, posisitve earnings, upgrades, price aboe previous close
            Bearish - negative news about the stock, price decrease, negative earnings, downgrades, price below previous close
            Neutral - no significant news, price stable, no change in earnings, no upgrades/downgrades, mixed signals or no strong directional news.
         4. Source of each of the news.
         5. Footer with a brief disclaimer.
         Keep professional tone and styling for the email.
         Remove '''html tags from the content"""),
         ("human","""Create the digest from the following stock summaries.\n\n {summaries}""")
    ])

    digest_chain = digest_prompt | llm

    today_date = date.today().strftime("%B %d, %Y")

    summaries_text = "\n\n".join([
        f"{s['ticker']} - {s['company']}\n"
        f"Price: {s['price_context']}\n"
        f"{s['summary']}\n\n"
        f"Sources: \n" + "\n".join(f"- {url}" for url in s.get("article_urls",[]))
        for s in state['summaries']
    ])

    response = digest_chain.invoke({'summaries': summaries_text, 'date':today_date})
    print("Digest Compiled.")
    return {"final_digest":response.content}

#---------------------------------------------------------------------
# NODE 5: Send email via Gmail
#---------------------------------------------------------------------
def send_email_node(state: StockNewsState) -> StockNewsState:
    """Send the compiled HTML digest via Gmail"""
    from services.email_service import GmailService

    gmail = GmailService()
    success = gmail.send_digest(state["final_digest"])
    return {"email_sent": success}
