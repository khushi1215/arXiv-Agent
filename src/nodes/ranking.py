import numpy as np

from src.utils.embeddings import embed_text, embed_texts


def _cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def ranking(state):
    query = state["user_input"]
    candidates = state["candidates"]

    query_vec = embed_text(query)
    abstracts = [c["abstract"] for c in candidates]
    abstract_vecs = embed_texts(abstracts)

    scores = [_cosine_sim(query_vec, vec) for vec in abstract_vecs]
    best_idx = int(np.argmax(scores))

    state["selected_paper"] = candidates[best_idx]
    return state
