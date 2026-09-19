# arXiv Paper Digest & QA Agent

A command line agent that takes a research topic or an arXiv paper, reads the paper, and gives you a structured briefing plus grounded answers to follow up questions.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Orchestration](https://img.shields.io/badge/orchestration-LangGraph-1c3c3c)
![LLM](https://img.shields.io/badge/LLM-Groq-fb542b)
![Vector DB](https://img.shields.io/badge/vector%20db-Chroma-6a4c93)

## What it does and why

Skimming through arXiv to figure out what's actually worth reading takes time. This agent does that first pass for you. Give it a topic, like "KV-cache compression for LLMs", or a specific arXiv ID or URL, and it will find the paper, read it, and hand back a structured briefing: what the paper is about, what problem it solves, how, what it found, and where it falls short. After that you can ask it free form questions about the paper and it answers using only what's actually in the paper text, not general knowledge about the topic.

## Architecture

The pipeline is built as an explicit state graph, not one long prompt. A shared state object moves through a sequence of nodes, each one reading from it and writing back into it.

```
                      query_understanding
                              |
                 -------------+-------------
                 |                          |
           (topic search)            (direct arxiv id)
                 |                          |
           arxiv_retrieval                  |
                 |                          |
              ranking                       |
                 |                          |
                 +-------------+------------+
                               |
                          fetch_parse
                               |
                          chunk_embed
                               |
                           summarize
                               |
                        [ briefing done ]
                               |
                          qa loop  (called directly, outside the graph,
                                    once per question the user types)
```

State carried through the graph:

- `user_input`, `intent` (topic or paper id)
- `candidates`, the list of papers found during a topic search
- `selected_paper`, the metadata of whichever paper was chosen
- `parsed_paper`, the extracted text and section breakdown
- `collection_name`, a reference to the paper's chunk embeddings in Chroma, not the vector store object itself
- `briefing`, the final structured output
- `qa_history`, the running list of questions asked and answers given
- `error`, set by any node that hits a failure it can't recover from, so the run stops cleanly instead of crashing

Two conditional branches exist in the graph. The first decides between the topic search path and the direct id path right after query understanding. The second checks whether a topic search actually returned any candidates before trying to rank them, so a vague topic that returns nothing fails gracefully with a clear message instead of crashing further down the pipeline.

The QA loop happens outside the compiled graph. Once a briefing exists, the CLI calls the QA node as a plain function, once per question, reusing the same state. See the design decisions section for why.

### Project structure

```
arxiv-agent/
├── app.py                      # entry point, runs the CLI
├── requirements.txt
├── .env.example
├── README.md
├── KNOWLEDGE.md
│
├── src/
│   ├── state.py                 # shared state schema
│   ├── graph.py                  # builds the state graph, nodes and edges
│   ├── cli.py                    # terminal input/output and formatting
│   │
│   ├── nodes/                    # one file per graph node
│   │   ├── query_understanding.py
│   │   ├── arxiv_retrieval.py
│   │   ├── ranking.py
│   │   ├── fetch_parse.py
│   │   ├── chunk_embed.py
│   │   ├── summarize.py
│   │   └── qa.py
│   │
│   └── utils/                    # reusable helpers the nodes call into
│       ├── arxiv_client.py       # wraps the official arXiv API
│       ├── pdf_parser.py          # PyMuPDF text extraction
│       ├── embeddings.py          # sentence-transformers wrapper
│       ├── vector_store.py        # Chroma collection access
│       ├── llm.py                 # Groq client
│       └── text_clean.py          # cleans up stray unicode punctuation
│
└── data/
    └── chroma_store/              # local vector db, created on first run
```

Each node in `src/nodes/` maps directly to a stage in the architecture diagram above, so it's easy to trace which file handles which part of the pipeline. Shared logic that more than one node needs, like calling the arXiv API or talking to Chroma, lives in `src/utils/` instead of being duplicated across nodes.

## Installation

Requires Python 3.10 or later and a free Groq API key from [console.groq.com](https://console.groq.com).

```bash
git clone https://github.com/khushi1215/arXiv-Agent.git
cd arxiv-agent
python -m venv venv
venv\Scripts\activate        # on Windows
source venv/bin/activate     # on macOS or Linux
pip install -r requirements.txt
```

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

Then open `.env` and set:

```
GROQ_API_KEY=your_actual_key_here
```

No paid API keys are required to run this project.

## Usage

Run the agent from the project root:

```bash
python app.py
```

You'll be asked for a topic or an arXiv ID or URL. A topic goes through search and ranking, an ID or URL skips straight to fetching that paper.

### Example run, topic search

Input: `231`

```
============================================================
231-Avoiding Involutions and Fibonacci Numbers
============================================================
Authors: Eric S. Egge, Toufik Mansour
arXiv ID: math/0209255v1   Published: 2002-09-19
Link: https://arxiv.org/pdf/math/0209255v1

Summary:
The paper provides exact enumerations for involutions that avoid the
pattern 231 or contain it exactly once, revealing that many of these
counts are given by k-generalized Fibonacci numbers.

Problem Statement:
Determine closed-form counts and generating functions for involutions
in S_n that avoid the pattern 231, or contain exactly one occurrence
of it, expressed in terms of k-generalized Fibonacci numbers.
```

(full briefing continues with method, key results, limitations, and suggested follow up questions)

Sample QA exchanges on this paper:

```
> what is a k-generalized Fibonacci number?

A k-generalized Fibonacci number is a term of the sequence F(k,n)
defined for a fixed integer k >= 0 by F(k,n) = 0 for n <= 0, F(k,1) = 1,
and for n >= 2, F(k,n) = F(k,n-1) + F(k,n-2) + ... + F(k,n-k). Each
term is the sum of the preceding k terms. When k = 2 this is the
ordinary Fibonacci sequence.

> what technique do they use to prove the formulas?

The authors use a combinatorial generating function approach. They
model the objects as tilings of a 1 x n rectangle, write functional
equations for the generating functions, and solve them. Several
proofs build directly on earlier results in the paper, for example
referencing Theorem 3.3 and Proposition 4.2 for the key combinatorial
decomposition.
```

### Example run, direct arXiv ID

Input: `2401.12345`

This skips search and ranking entirely and goes straight to fetching that specific paper, "Distributionally Robust Receive Combining" by Wang, Dai, and Li.

## Tech stack

| Tool | Role |
|---|---|
| LangGraph | Builds the explicit state graph, nodes, edges, and shared state |
| Groq (openai/gpt-oss-120b) | LLM used for both the briefing generation and grounded QA |
| Chroma | Local vector database, stores chunk embeddings per paper, persists to disk |
| sentence-transformers (all-MiniLM-L6-v2) | Embedding model, used for both abstract-level ranking and chunk retrieval |
| PyMuPDF | Extracts text and page content from paper PDFs |
| arxiv (Python package) | Wraps the official arXiv Atom API for search and metadata lookup, no scraping |

Rate limits: Groq's free tier has per-minute and per-day token limits that vary by model. If you hit a rate limit mid session, wait a minute and try again. Details at [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits).

## Design decisions and tradeoffs

**Orchestration.** Chose LangGraph over writing a custom Python state machine or using LlamaIndex Workflows. It gives the explicit state graph this project needs by design, without writing that machinery from scratch.

**Single dense retrieval, not hybrid.** QA uses embedding similarity search only, not a combination of keyword and embedding search. Paper questions tend to be conceptual rather than needing exact keyword matches, so this covers most cases while staying simple. The tradeoff is a question asking for an exact number or specific term the paper reported might retrieve a topically related chunk that doesn't contain the literal figure.

**Fixed size chunking over section based chunking.** Chunks are 1000 characters with 150 character overlap, not split along the parser's detected sections. The section detection is a heuristic and not always reliable, so chunking independently of it keeps retrieval consistent even when section splitting misses the mark.

**QA loop outside the compiled graph.** Once a briefing is generated, the graph run ends. The CLI then calls the QA node directly, once per question, instead of looping QA inside the graph itself. Everything upstream of QA (search, fetch, parse, chunk, embed) only needs to happen once per paper, so there's no benefit to routing repeat questions back through the whole graph.

**Large papers get truncated, not rejected.** Extracted text is capped at 120,000 characters before chunking. This keeps embedding and LLM calls fast and bounded, but means a very long paper's later sections might not make it into the briefing or the QA context.

**What would change with more time.** Hybrid retrieval (embeddings plus keyword search) would likely improve QA on questions asking for exact figures. Section detection could use a more robust method than header name matching, possibly based on font size or layout position extracted directly from the PDF rather than plain text heuristics. Automated tests for each node, currently this was tested manually end to end rather than with a test suite, given the project time box.

**Known limitations, stated honestly.** Section splitting can fail on papers with unusual formatting or two column layouts. PDF parsing was tested successfully on standard text based papers, a scanned or image only PDF would raise a clear error rather than crash, per the code, but this path wasn't manually exercised against a real scanned paper during testing. Single dense retrieval may occasionally miss exact-figure questions as noted above.