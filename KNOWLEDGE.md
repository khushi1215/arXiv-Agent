# KNOWLEDGE.md

## Project definition

An agent that takes a research topic or a specific arXiv paper, reads the paper, writes a structured briefing explaining what it's about, and then answers follow up questions about it, grounded in the actual paper text.

## Tech stack decisions

### Orchestration: LangGraph

Considered a custom Python state machine and LlamaIndex Workflows. Went with LangGraph because it gives an explicit state graph (nodes, edges, shared state) out of the box, which the project needs anyway, and because it's the same ecosystem as an earlier project, so less new surface area to debug during a short time box.

### LLM: Groq

Considered Gemini free tier and a local Ollama model. Went with Groq for speed during iteration and because a free tier key was already available from an earlier project. Tradeoff: available models on a given account can differ from what's in Groq's docs, see the model access entry below.

### Vector DB: Chroma

Considered FAISS and LanceDB. Went with Chroma for zero setup and because it persists to disk automatically, so a paper doesn't need to be re-parsed and re-embedded if the same paper comes up again in a later run.

### Embeddings: sentence-transformers, all-MiniLM-L6-v2

No serious alternative considered here, this is a standard small fast model, good enough for abstract-level ranking and chunk retrieval, no need for a heavier model given the accuracy bar this project needs.

### PDF parsing: PyMuPDF

Considered pdfplumber. Went with PyMuPDF for speed and because it handles multi-column academic PDF layouts reasonably well.

### arXiv retrieval: the arxiv python package

Considered hitting the Atom API directly with requests and parsing XML by hand. Went with the arxiv package since it's a thin wrapper over the same official API, not scraping, and it saves writing and debugging XML parsing code that doesn't add any real value to the project.

### Retrieval strategy: single dense retrieval, not hybrid

Considered hybrid retrieval (BM25 keyword search plus embeddings), which was used in an earlier project. Decided against it here. A paper's questions tend to be conceptual (what method, what limitations) rather than needing exact keyword matches on things like ticker symbols or invoice numbers, so plain embedding similarity should cover most cases. Named as a tradeoff, hybrid would likely help on questions asking for an exact number or metric the paper reported.

## Data and system overview

State is a single dict-like object (state.py, AgentState) that flows through every node. Each node reads what it needs and writes its output back into the same object. Early assumption: state should stay lightweight and serializable, so the Chroma collection itself is never stored in state, just its name, and it gets looked up again when needed.

Chunking is fixed size, 1000 characters with 150 character overlap, not paragraph or sentence based. Simpler and more predictable than depending on the section-splitting heuristic being accurate. Overlap exists so an answer that straddles a chunk boundary doesn't get cut in half.

Large papers get truncated at 120,000 extracted characters before chunking, to keep embedding and LLM calls fast and bounded. This means very long papers could lose their later sections from the briefing and QA context.

QA loop runs outside the compiled LangGraph graph. Once the briefing is generated the graph run ends. The CLI then calls the QA node function directly, once per question typed, reusing the same state object. Looping this inside the graph itself would mean the graph either recompiles per question or sits paused waiting on user input, both worse than just calling a function directly since nothing upstream of QA needs to rerun per question.

## Discoveries and challenges

Groq model `llama-3.3-70b-versatile` is documented on Groq's own docs site as an available production model, but calling it returned a 404 model_not_found error on this account. Checked available models directly against `/openai/v1/models` and it wasn't in the list for this key. Switched to `openai/gpt-oss-120b`, which was available. Lesson: don't trust a provider's public docs for what's actually enabled on a given account, check the live model list first.

PyMuPDF's `fitz` import name triggered a deprecation warning on first run. Switched the import to `pymupdf as fitz` to keep the rest of the code unchanged while using the non-deprecated import path.

A transient network error during a live test (DNS resolution failure calling the Groq API) crashed the whole QA session on one bad question, even though the briefing had already been generated successfully. Wrapped the QA node's LLM call in a try/except so a single failed question reports an error and lets the loop continue, instead of losing the whole session over one network blip.

## Honest revisions

Original LLM choice was Groq without a specific model pinned down. First model tried, llama-3.3-70b-versatile, is listed on Groq's public docs as a production model but returned a 404 not found error on the account actually being used for this project. This entry supersedes that original assumption. Confirmed working model for this account is openai/gpt-oss-120b, checked directly against the live models endpoint rather than the docs.

## Limitations

Section splitting in the PDF parser is a heuristic based on matching short lines against a fixed list of common header names. Works on typical arXiv formatting, will miss papers with unusual structure or where the two column layout jumbles extracted text order.

Truncating papers at 120,000 characters means the briefing and QA grounding may not include later sections of very long papers.

Single dense retrieval, not hybrid, means questions asking for an exact number or specific term might retrieve a chunk that's topically related but doesn't contain the literal figure asked about.

## Changelog

- 2026-09-18: Initial architecture and tech stack decisions made, LangGraph, Groq, Chroma, sentence-transformers, PyMuPDF, arxiv package
- 2026-09-18: Full node pipeline written, query understanding, arxiv retrieval, ranking, fetch and parse, chunk and embed, summarize, qa
- 2026-09-18: CLI and entry point written
- 2026-09-18: Groq model swapped from llama-3.3-70b-versatile to openai/gpt-oss-120b after confirming actual account access
- 2026-09-18: Added error handling around the QA node's LLM call after a live test hit a transient network failure mid session
