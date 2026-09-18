from src.utils.pdf_parser import download_pdf, parse_pdf

# cap on total extracted characters we carry forward, keeps huge papers
# from blowing up downstream chunking/embedding time and llm context
MAX_CHARS = 120_000


def fetch_parse(state):
    paper = state["selected_paper"]

    try:
        pdf_bytes = download_pdf(paper["pdf_url"])
    except Exception as e:
        state["error"] = f"couldn't download the pdf: {e}"
        return state

    try:
        parsed = parse_pdf(pdf_bytes)
    except Exception as e:
        state["error"] = f"couldn't parse the pdf: {e}"
        return state

    if len(parsed["full_text"]) > MAX_CHARS:
        parsed["full_text"] = parsed["full_text"][:MAX_CHARS]

    state["parsed_paper"] = parsed
    return state
