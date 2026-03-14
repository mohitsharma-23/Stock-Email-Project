import yfinance as yf
import os
from langchain_core.tools import tool


@tool
def fetch_stock_price(ticker: str) -> dict:
    "Tool to fetch the stock price and price targets for the specific stock"
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.fast_info

        current_price = round(stock_info.last_price,2)
        prev_close = round(stock_info.previous_close,2)
        day_high = round(stock_info.day_high,2)
        day_low = round(stock_info.day_low,2)
        year_high = round(stock_info.year_high,2)
        year_low = round(stock_info.year_low,2)
        day_change_pct = round((current_price - prev_close)/prev_close *100, 2)
        # day_change_pct = round((stock_info.last_price- stock_info.previous_close)/stock_info.previous_close *100, 2)
        return {
            "ticker": ticker,
            "current_price": current_price,
            "prev_close": prev_close,
            "day_high": day_high,
            "day_low": day_low,
            "year_high": year_high,
            "year_low": year_low,
            "day_change_pct": day_change_pct
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "current_price": "N/A",
            "prev_close": "N/A",
            "day_high": "N/A",
            "day_low": "N/A",
            "year_high": "N/A",
            "year_low": "N/A",
            "day_change_pct": "N/A"
        }

@tool
def fetch_stock_news(ticker: str) -> dict:
    "Fetches any stock news headlines from the yahoo finance"
    try:
        ticker_yf = yf.Ticker(ticker=ticker)
        news = ticker_yf.get_news(count=5, tab='news')

        #Initializing the list of things to return
        title_list = []
        description_list = []
        canonical_url_list = []
        content_type_list =[]

        articles = [] # this will contain all the news for the stock tickers

        for article in news:
            articles.append({
                "ticker":ticker,
                "title": article['content'].get("title", "No title"),
                "description": article['content'].get("description", "No description available"),
                "url": article['content']['canonicalUrl'].get("url","No url available"),
                "content_type": article['content'].get("contentType", "No content type available")
            })
        return articles
        # for article in news:
        #     title_list.append(article['content'].get("title"))
        #     description_list.append(article['content'].get("description"))
        #     canonical_url_list.append(article['content']['canonicalUrl'].get("url"))
        #     content_type_list.append(article['content'].get('contentType'))
        # return {
        #     "ticker": ticker,
        #     "title": title_list,
        #     "description": description_list,
        #     "url": canonical_url_list,
        #     "content_type": content_type_list
        # }
    except Exception as e:
        return {
            "ticker": ticker,
            "title": "N/A",
            "description": "N/A",
            "url": "N/A",
            "content_type": "N/A",
            "error": str(e)
        }


ticker = 'mu'
info = fetch_stock_price.invoke(
    {
        "ticker":ticker
    }
)
stock_news = fetch_stock_news.invoke(
    {
        "ticker": ticker
    }
)