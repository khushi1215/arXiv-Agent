import arxiv

_client = arxiv.Client()


def search_papers(query, max_results=5):
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    return [_to_metadata(r) for r in _client.results(search)]


def get_paper_by_id(arxiv_id):
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(_client.results(search))
    if not results:
        return None
    return _to_metadata(results[0])


def _to_metadata(result):
    return {
        "arxiv_id": result.get_short_id(),
        "title": result.title.strip(),
        "authors": [a.name for a in result.authors],
        "abstract": result.summary.strip().replace("\n", " "),
        "pdf_url": result.pdf_url,
        "published": result.published.strftime("%Y-%m-%d"),
        "categories": result.categories,
    }
