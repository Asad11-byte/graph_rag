class GraphRAGService:
    """
    Main GraphRAG pipeline.

    Flow
    ----
    User Question
          ↓
    LLM Entity Extraction
          ↓
    Graph Entity Matching
          ↓
    Community Search
          ↓
    Graph Retrieval
          ↓
    LLM Answer Generation
    """

    def __init__(
        self,
        graph_searcher,
        community_searcher,
        groq_service,
    ):

        self.graph_searcher = graph_searcher

        self.community_searcher = community_searcher

        self.groq_service = groq_service

    # =====================================================
    # Main Question Answer
    # =====================================================

    def answer(
        self,
        question: str,
    ):

        print(
            "\n========== GRAPHRAG QUERY ==========\n"
        )

        print(
            f"Question : {question}"
        )

        # ---------------------------------
        # Step 1 : Extract entity using LLM
        # ---------------------------------

        entity = self.groq_service.extract_entity(
            question
        )

        print(
            f"Extracted Entity : {entity}"
        )

        # ---------------------------------
        # Step 2 : Match entity in graph
        # ---------------------------------

        matched_entity = self.graph_searcher.find_entity(
            entity
        )

        if matched_entity is None:

            return {
                "error":
                f"No graph entity found for '{entity}'."
            }

        print(
            f"Matched Entity : {matched_entity}"
        )

        # ---------------------------------
        # Step 3 : Community Search
        # ---------------------------------

        community = self.community_searcher.search(
            matched_entity
        )

        community_id = None

        if community:

            community_id = community["community_id"]

            print(
                f"Community : {community_id}"
            )

        # ---------------------------------
        # Step 4 : Retrieve Graph Context
        # ---------------------------------

        context = self.graph_searcher.retrieve_context(
            matched_entity
        )

        print(
            "\nRetrieved Context:\n"
        )

        print(context)

        # ---------------------------------
        # Step 5 : Generate Final Answer
        # ---------------------------------

        answer = self.groq_service.answer_question(
            context=context,
            question=question,
        )

        print(
            "\n========== FINAL ANSWER ==========\n"
        )

        print(answer)

        # ---------------------------------
        # Step 6 : Return structured result
        # ---------------------------------

        return {

            "question": question,

            "entity": entity,

            "matched_entity": matched_entity,

            "community_id": community_id,

            "context": context,

            "answer": answer,
        }