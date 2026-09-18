from src.nodes.qa import answer_question


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_briefing(briefing):
    print_header(briefing.get("title", "Untitled"))
    print(f"Authors: {', '.join(briefing.get('authors', []))}")
    print(f"arXiv ID: {briefing.get('arxiv_id', 'n/a')}   Published: {briefing.get('published', 'n/a')}")
    print(f"Link: {briefing.get('link', 'n/a')}")

    print("\nSummary:")
    print(briefing.get("summary", ""))

    print("\nProblem Statement:")
    print(briefing.get("problem_statement", ""))

    print("\nMethod:")
    for point in briefing.get("method", []):
        print(f"  - {point}")

    print("\nKey Results:")
    for point in briefing.get("key_results", []):
        print(f"  - {point}")

    print("\nLimitations:")
    for point in briefing.get("limitations", []):
        print(f"  - {point}")

    print("\nSuggested follow-up questions:")
    for q in briefing.get("followup_questions", []):
        print(f"  - {q}")
    print()


def qa_loop(state):
    print_header("Ask questions about this paper (type 'exit', 'quit', or 'q' to stop)")
    while True:
        question = input("\n> ").strip()
        if question.lower() in ("exit", "quit", "q"):
            break
        if not question:
            continue
        answer = answer_question(state, question)
        print(f"\n{answer}")
