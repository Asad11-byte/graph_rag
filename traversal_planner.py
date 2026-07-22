from dataclasses import dataclass
from typing import Optional


# ==========================================================
# Traversal Plan
# ==========================================================

@dataclass
class TraversalPlan:
    """
    Describes how the graph should be traversed
    for answering a specific question.
    """

    depth: int

    direction: str

    preferred_relations: Optional[list[str]] = None


# ==========================================================
# Traversal Planner
# ==========================================================

class TraversalPlanner:
    """
    Decide how the graph should be explored
    based on the user's question.
    """

    def __init__(self):

        self.relation_keywords = {

            "developed_by": [
                "develop",
                "developer",
                "created",
                "creator",
                "made",
                "studio",
            ],

            "published_by": [
                "publish",
                "publisher",
            ],

            "uses_engine": [
                "engine",
                "technology",
            ],

            "genre": [
                "genre",
                "type",
                "category",
            ],

            "released_in": [
                "release",
                "released",
                "year",
                "date",
                "launch",
            ],

            "has_expansion": [
                "expansion",
                "dlc",
                "addon",
                "extension",
            ],

        }

    # ======================================================
    # Build Traversal Plan
    # ======================================================

    def plan(self, question: str) -> TraversalPlan:

        question = question.lower()

        # --------------------------------------------------
        # Tell me everything
        # --------------------------------------------------

        if any(
            word in question
            for word in [
                "everything",
                "all",
                "about",
                "describe",
                "information",
            ]
        ):

            return TraversalPlan(
                depth=3,
                direction="both",
                preferred_relations=None,
            )

        # --------------------------------------------------
        # Find relation keywords
        # --------------------------------------------------

        matched_relations = []

        for relation, keywords in self.relation_keywords.items():

            for keyword in keywords:

                if keyword in question:

                    matched_relations.append(relation)

                    break

        # --------------------------------------------------
        # Choose traversal depth
        # --------------------------------------------------

        if len(matched_relations) == 0:

            depth = 2

        elif len(matched_relations) == 1:

            depth = 1

        else:

            depth = 2

        # --------------------------------------------------
        # Decide traversal direction
        # --------------------------------------------------

        direction = "out"

        if any(
            word in question
            for word in [
                "who",
                "which",
                "what",
                "when",
                "where",
            ]
        ):
            direction = "out"

        if any(
            word in question
            for word in [
                "games using",
                "games developed by",
                "games published by",
            ]
        ):
            direction = "both"

        return TraversalPlan(
            depth=depth,
            direction=direction,
            preferred_relations=matched_relations or None,
        )

    # ======================================================
    # Pretty Print
    # ======================================================

    def print_plan(self, plan: TraversalPlan):

        print("\n========== TRAVERSAL PLAN ==========\n")

        print(f"Depth      : {plan.depth}")

        print(f"Direction  : {plan.direction}")

        print(
            "Relations  :",
            plan.preferred_relations
            if plan.preferred_relations
            else "All"
        )

        print("\n====================================\n")