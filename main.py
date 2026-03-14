import os
from dotenv import load_dotenv

load_dotenv()

from agent.graph import agent_graph

def run_agent():
    print("\n" + "=" * 50)
    print(" Stock News Agent Starting...")
    print("=" * 50)

    initial_state = {
        "stocks": [],
        "stock_news":[],
        "summaries":[],
        "final_digest":"",
        "email_sent":False,
        "errors": []
    }

    result = agent_graph.invoke(initial_state)

    print("\n" + "=" * 50)
    print("Agent execution summary....")
    print("=" * 50)
    print(f" Stocks fetched: {len(result.get('summaries',[]))}")

    # for stock in result.get('summaries'):
    #     print(f" Stock news for {stock['ticker']} ===========")
    #     print(f"{stock['summary']} \n\n")
    # print(f"Summary for stocks: \n {result.get('summaries')}")

if __name__=="__main__":
    run_agent()