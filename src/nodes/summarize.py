import json

from src.utils.llm import get_llm
from src.utils.text_clean import clean_briefing

PROMPT = """You are briefing a busy researcher on a paper they haven't read yet.

Paper title: {title}
Authors: {authors}
Abstract: {abstract}

Paper sections (may be partial or imperfectly split):
{sections_text}

Based on the above, write a structured briefing. Respond with ONLY valid JSON, no markdown fences, no extra text, in exactly this shape:

{{
  "summary": "one paragraph in plain english explaining why this paper matters",
  "problem_statement": "what problem is this paper solving",
  "method": ["point 1", "point 2"],
  "key_results": ["point 1", "point 2"],
  "limitations": ["point 1", "point 2"],
  "followup_questions": ["question 1", "question 2", "question 3"]
}}

Be honest about limitations. If the paper doesn't state any explicitly, infer likely ones from the method and say so rather than leaving it empty.

Use plain straight quotes and plain hyphens, not curly quotes or dashes.
"""


def _format_sections(sections, max_chars=6000):
    parts = []
    total = 0
    for name, text in sections.items():
        snippet = text[:1500]
        parts.append(f"[{name}]\n{snippet}")
        total += len(snippet)
        if total > max_chars:
            break
    return "\n\n".join(parts)


def summarize(state):
    paper = state["selected_paper"]
    parsed = state["parsed_paper"]

    prompt = PROMPT.format(
        title=paper["title"],
        authors=", ".join(paper["authors"]),
        abstract=paper["abstract"],
        sections_text=_format_sections(parsed["sections"]),
    )

    response = get_llm().invoke(prompt)
    raw = response.content.strip()

    # models sometimes wrap the json in markdown fences even when told not to
    if raw.startswith("```"):
        raw = raw.strip("`")
        if "\n" in raw:
            raw = raw.split("\n", 1)[1]
        if raw.lower().startswith("json"):
            raw = raw[4:]

    try:
        briefing = json.loads(raw)
    except json.JSONDecodeError as e:
        state["error"] = f"model didn't return valid json for the briefing: {e}"
        return state

    briefing["title"] = paper["title"]
    briefing["authors"] = paper["authors"]
    briefing["arxiv_id"] = paper["arxiv_id"]
    briefing["published"] = paper["published"]
    briefing["link"] = paper["pdf_url"]

    state["briefing"] = clean_briefing(briefing)
    return state
