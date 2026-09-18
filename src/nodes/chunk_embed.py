from src.utils.embeddings import embed_texts
from src.utils.vector_store import get_collection

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def _chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_embed(state):
    paper = state["selected_paper"]
    full_text = state["parsed_paper"]["full_text"]

    chunks = _chunk_text(full_text)
    if not chunks:
        state["error"] = "nothing to chunk, parsed text came back empty"
        return state

    vectors = embed_texts(chunks)

    # chroma collection names can't have dots or slashes, arxiv ids have both
    collection_name = paper["arxiv_id"].replace(".", "_").replace("/", "_")
    collection = get_collection(collection_name)

    # if we've already processed this paper before, clear the old chunks
    # out first so we don't end up with duplicates
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=[f"{collection_name}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=[v.tolist() for v in vectors],
    )

    state["collection_name"] = collection_name
    return state
