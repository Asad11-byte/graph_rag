from games_data import GAME_DOCUMENTS
from graph_builder import GraphBuilder
from graph_search import GraphSearcher
from groq_service import GroqService
from traversal_planner import TraversalPlanner
from community_detector import CommunityDetector


# ==========================================================
# Graph Construction
# ==========================================================

def build_graph(groq: GroqService) -> GraphBuilder:
    """
    Build the Knowledge Graph from all game documents.
    """

    builder = GraphBuilder()

    all_triples = []

    print("\n========== GRAPH CONSTRUCTION ==========\n")

    for index, document in enumerate(GAME_DOCUMENTS, start=1):

        print(f"Processing document {index}...")

        try:

            triples = groq.extract_triples(document)

            print(f"✓ Extracted {len(triples)} triples")

            all_triples.extend(triples)

        except Exception as error:

            print(f"❌ Failed to process document {index}")

            print(error)

    builder.build(all_triples)

    builder.print_statistics()

    builder.save_json()

    builder.save_graph_html()

    print("\n✓ Knowledge Graph successfully built.\n")

    return builder


# ==========================================================
# Community Detection
# ==========================================================

def detect_communities(
    builder: GraphBuilder,
) -> CommunityDetector:
    """
    Detect graph communities using
    the Louvain algorithm.
    """

    detector = CommunityDetector(builder.graph)

    detector.detect()

    detector.print_statistics()

    detector.print_communities()

    detector.save_json()

    return detector


# ==========================================================
# GraphRAG Question Answering
# ==========================================================

def ask_question(

    groq: GroqService,

    planner: TraversalPlanner,

    searcher: GraphSearcher,

):
    """
    Execute one GraphRAG query.
    """

    while True:

        question = input(
            "\nAsk a question ('exit' to quit): "
        ).strip()

        if question.lower() == "exit":

            print("\nGoodbye!\n")

            break

        if not question:

            print("\nQuestion cannot be empty.\n")

            continue

        # --------------------------------------------------
        # Entity Extraction
        # --------------------------------------------------

        entity = groq.extract_entity(question)

        print("\n========== ENTITY EXTRACTION ==========\n")

        print(f"Question : {question}")

        print(f"Entity   : {entity}")

        # --------------------------------------------------
        # Traversal Planning
        # --------------------------------------------------

        plan = planner.plan(question)

        planner.print_plan(plan)

        # --------------------------------------------------
        # Graph Search
        # --------------------------------------------------

        matched = searcher.find_entity(entity)

        if matched is None:

            print("\n❌ Entity not found in Knowledge Graph.\n")

            continue

        print("\n========== GRAPH SEARCH ==========\n")

        print(f"Matched Entity : {matched}")

        # --------------------------------------------------
        # Context Retrieval
        # --------------------------------------------------

        context = searcher.retrieve_context(

            start_entity=matched,

            max_depth=plan.depth,

            direction=plan.direction,

            preferred_relations=plan.preferred_relations,

        )

        print("\n========== RETRIEVED CONTEXT ==========\n")

        print(context)

        # --------------------------------------------------
        # LLM Answer
        # --------------------------------------------------

        print("\n========== FINAL ANSWER ==========\n")

        answer = groq.answer_question(

            context=context,

            question=question,

        )

        print(answer)

        print("\n==================================\n")


# ==========================================================
# Main
# ==========================================================

def main():
    """
    Phase 4

    Pipeline

    Documents
        ↓
    Triple Extraction
        ↓
    Knowledge Graph
        ↓
    Community Detection
        ↓
    Entity Extraction
        ↓
    Traversal Planning
        ↓
    Dynamic Multi-Hop Traversal
        ↓
    Context Generation
        ↓
    Groq
        ↓
    Final Answer
    """

    # ----------------------------------------------
    # Initialize Services
    # ----------------------------------------------

    groq = GroqService()

    planner = TraversalPlanner()

    # ----------------------------------------------
    # Build Knowledge Graph
    # ----------------------------------------------

    builder = build_graph(groq)

    # ----------------------------------------------
    # Detect Communities
    # ----------------------------------------------

    detector = detect_communities(builder)

    print(
        f"\n✓ Community Detection Complete "
        f"({len(detector.communities)} communities found)\n"
    )

    # ----------------------------------------------
    # Graph Search Engine
    # ----------------------------------------------

    searcher = GraphSearcher(builder.graph)

    # ----------------------------------------------
    # Interactive QA
    # ----------------------------------------------

    ask_question(

        groq=groq,

        planner=planner,

        searcher=searcher,

    )


if __name__ == "__main__":

    main()