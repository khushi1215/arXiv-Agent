from sentence_transformers import SentenceTransformer

# small and fast, good enough for abstract-level similarity and chunk retrieval
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text):
    return get_embedder().encode(text)


def embed_texts(texts):
    return get_embedder().encode(texts)
