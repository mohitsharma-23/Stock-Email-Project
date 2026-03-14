from langgraph.graph import StateGraph, END

from agent.state import StockNewsState
from agent.nodes import load_stocks_node, fetch_news_node, summarize_node, compile_digest_node, send_email_node

def build_graph() -> StateGraph:
    graph = StateGraph(state_schema=StockNewsState)

    #Setup the nodes
    graph.add_node("load_stocks", load_stocks_node)
    graph.add_node("fetch_news", fetch_news_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("compile_digest", compile_digest_node)
    graph.add_node("send_email", send_email_node)

    #Define the edges/connections
    graph.set_entry_point("load_stocks")
    graph.add_edge("load_stocks","fetch_news")
    graph.add_edge("fetch_news","summarize")
    graph.add_edge("summarize","compile_digest")
    graph.add_edge("compile_digest","send_email")

    return graph.compile()

agent_graph = build_graph()