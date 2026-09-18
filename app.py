from src.cli import print_header, print_briefing, qa_loop
from src.graph import build_graph
from src.state import new_state


def main():
    print_header("arXiv Paper Digest & QA Agent")
    user_input = input("\nEnter a topic or an arXiv ID/URL: ").strip()

    if not user_input:
        print("nothing entered, exiting")
        return

    print("\nworking on it, first run can take a bit while the embedding model downloads...")

    graph = build_graph()
    state = graph.invoke(new_state(user_input))

    if state.get("error"):
        print(f"\nsomething went wrong: {state['error']}")
        return

    if not state.get("briefing"):
        print("\nno briefing came out of that, exiting")
        return

    print_briefing(state["briefing"])
    qa_loop(state)


if __name__ == "__main__":
    main()
