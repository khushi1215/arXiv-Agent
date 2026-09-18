import chromadb

CHROMA_PATH = "data/chroma_store"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def get_collection(name):
    return get_client().get_or_create_collection(name=name)
