import re

from src.utils.arxiv_client import get_paper_by_id

# matches things like 2401.12345, 2401.12345v2, or the old style hep-th/9901001
ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5}(v\d+)?|[a-z\-]+/\d{7})")


def _extract_id(text):
    text = text.strip()
    # strip a full arxiv url down to just the id
    if "arxiv.org" in text:
        text = text.rstrip("/").split("/")[-1]
        text = text.replace(".pdf", "")

    match = ARXIV_ID_PATTERN.search(text)
    return match.group(1) if match else None


def query_understanding(state):
    user_input = state["user_input"]
    arxiv_id = _extract_id(user_input)

    if arxiv_id:
        paper = get_paper_by_id(arxiv_id)
        if paper is None:
            state["error"] = f"couldn't find a paper with id {arxiv_id}"
            return state
        state["intent"] = "paper_id"
        state["selected_paper"] = paper
        return state

    # not an id, treat it as a topic search
    state["intent"] = "topic"
    return state
