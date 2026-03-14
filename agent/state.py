from typing import TypedDict, Annotated
from operator import add

class StockNewsState(TypedDict):
    stocks : list[dict]                             # Input wathlist
    stock_news : Annotated[list[dict], add]         # Stock price and news
    summaries : Annotated[list[dict], add]          # Per stock summaries
    final_digest: str                               # Final email body
    email_sent : bool                               # Status flag
    errors : Annotated[list[dict], add]             # Error logs          