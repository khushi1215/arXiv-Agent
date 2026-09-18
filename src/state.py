from typing import TypedDict, Optional, List, Dict, Any


class PaperMetadata(TypedDict):
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    published: str
    categories: List[str]


class ParsedPaper(TypedDict):
    full_text: str
    sections: Dict[str, str]
    num_pages: int


class QAExchange(TypedDict):
    question: str
    answer: str


# this gets passed between every node in the graph, each node reads
# what it needs and writes its own output back into it
class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]          # "topic" or "paper_id"
    candidates: List[PaperMetadata]
    selected_paper: Optional[PaperMetadata]
    parsed_paper: Optional[ParsedPaper]
    collection_name: Optional[str]  # chroma collection id, not the object itself
    briefing: Optional[Dict[str, Any]]
    qa_history: List[QAExchange]
    error: Optional[str]


def new_state(user_input: str) -> AgentState:
    return AgentState(
        user_input=user_input,
        intent=None,
        candidates=[],
        selected_paper=None,
        parsed_paper=None,
        collection_name=None,
        briefing=None,
        qa_history=[],
        error=None,
    )
