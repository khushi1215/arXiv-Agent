from src.utils.arxiv_client import search_papers

MAX_CANDIDATES = 8


def arxiv_retrieval(state):
    query = state["user_input"]
    results = search_papers(query, max_results=MAX_CANDIDATES)

    if not results:
        state["error"] = (
            f"no papers found for '{query}', try rephrasing or using broader terms"
        )
        state["candidates"] = []
        return state

    state["candidates"] = results
    return state
