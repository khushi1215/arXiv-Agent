from src.utils.embeddings import embed_text
from src.utils.llm import get_llm
from src.utils.text_clean import clean_text
from src.utils.vector_store import get_collection

TOP_K = 5

PROMPT = """Answer the question using ONLY the context below, which is pulled from the paper "{title}".

Context:
{context}

Question: {question}

If the context doesn't contain enough information to answer, say so plainly instead of guessing. Don't use outside knowledge about this topic, only what's in the context above.

Use plain straight quotes and plain hyphens, not curly quotes or dashes.

Answer:"""


def answer_question(state, question):
    collection = get_collection(state["collection_name"])
    query_vec = embed_text(question)

    results = collection.query(query_embeddings=[query_vec.tolist()], n_results=TOP_K)
    chunks = results["documents"][0] if results["documents"] else []

    if not chunks:
        answer = "I couldn't find anything relevant to that in the paper."
    else:
        context = "\n\n---\n\n".join(chunks)
        prompt = PROMPT.format(
            title=state["selected_paper"]["title"],
            context=context,
            question=question,
        )
        try:
            answer = clean_text(get_llm().invoke(prompt).content.strip())
        except Exception as e:
            answer = f"couldn't get an answer right now ({e}), try asking again"

    state["qa_history"].append({"question": question, "answer": answer})
    return answer
