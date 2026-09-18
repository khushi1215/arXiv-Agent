from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.nodes.query_understanding import query_understanding
from src.nodes.arxiv_retrieval import arxiv_retrieval
from src.nodes.ranking import ranking
from src.nodes.fetch_parse import fetch_parse
from src.nodes.chunk_embed import chunk_embed
from src.nodes.summarize import summarize


def route_after_query_understanding(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    if state["intent"] == "topic":
        return "search"
    return "direct"


def route_after_retrieval(state: AgentState) -> str:
    # zero candidates means the topic search came up empty, nothing to rank
    if state.get("error") or not state["candidates"]:
        return "end"
    return "rank"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("query_understanding", query_understanding)
    graph.add_node("arxiv_retrieval", arxiv_retrieval)
    graph.add_node("ranking", ranking)
    graph.add_node("fetch_parse", fetch_parse)
    graph.add_node("chunk_embed", chunk_embed)
    graph.add_node("summarize", summarize)

    graph.set_entry_point("query_understanding")

    graph.add_conditional_edges(
        "query_understanding",
        route_after_query_understanding,
        {"search": "arxiv_retrieval", "direct": "fetch_parse", "end": END},
    )

    graph.add_conditional_edges(
        "arxiv_retrieval",
        route_after_retrieval,
        {"rank": "ranking", "end": END},
    )

    graph.add_edge("ranking", "fetch_parse")
    graph.add_edge("fetch_parse", "chunk_embed")
    graph.add_edge("chunk_embed", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# note: the QA loop is NOT part of this graph. once summarize runs and we
# have a briefing + a chroma collection, the CLI calls the qa node directly
# in a loop for each question the user types. putting QA inside the graph
# itself would mean recompiling/reinvoking the whole graph per question,
# which is wasteful since nothing upstream of QA needs to rerun. this is
# called out as a design decision in the README.
