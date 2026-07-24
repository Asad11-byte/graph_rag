import re
from collections import deque
from difflib import SequenceMatcher, get_close_matches
from typing import Optional

import networkx as nx


# =====================================================
# Entity Name Normalization Helpers
# =====================================================

STOPWORDS = {"the", "of", "and", "a", "an", "in", "on"}

ROMAN_TO_ARABIC = {
    "i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5",
    "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10",
    "xi": "11", "xii": "12", "xiii": "13", "xiv": "14", "xv": "15",
    "xvi": "16", "xvii": "17", "xviii": "18", "xix": "19", "xx": "20",
}
ARABIC_TO_ROMAN = {v: k for k, v in ROMAN_TO_ARABIC.items()}


def normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""

    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_trailing_numeral(tokens: list[str]):
    """
    If the last token is a number or roman numeral, split it off and
    return (remaining_tokens, arabic_numeral_str_or_None).
    """

    if not tokens:
        return tokens, None

    last = tokens[-1]

    if last.isdigit():
        return tokens[:-1], last

    if last in ROMAN_TO_ARABIC:
        return tokens[:-1], ROMAN_TO_ARABIC[last]

    return tokens, None


def build_match_candidates(raw_text: str) -> set[str]:
    """
    Given a raw entity name or query, build a set of normalized string
    variants that should all be considered equivalent:
      - the plain normalized text (numbers and roman numerals both kept)
      - the acronym form (e.g. "grand theft auto v" -> "gta v" / "gta 5")
    This lets "Grand Theft Auto V", "gta v", and "gta 5" all resolve to
    the same node.
    """

    normalized = normalize_text(raw_text)
    tokens = normalized.split()

    words, numeral = split_trailing_numeral(tokens)

    candidates = {normalized}

    # Acronym from initials of significant words (e.g. "grand theft auto" -> "gta")
    significant = [w for w in words if w not in STOPWORDS and w]

    if len(significant) >= 2:
        acronym = "".join(w[0] for w in significant)

        if numeral:
            candidates.add(f"{acronym} {numeral}")
            candidates.add(f"{acronym}{numeral}")

            if numeral in ARABIC_TO_ROMAN:
                roman = ARABIC_TO_ROMAN[numeral]
                candidates.add(f"{acronym} {roman}")
                candidates.add(f"{acronym}{roman}")
        else:
            candidates.add(acronym)

    # Also add a version with the numeral swapped digit<->roman, keeping full words
    if numeral:
        base = " ".join(words)

        candidates.add(f"{base} {numeral}".strip())

        if numeral in ARABIC_TO_ROMAN:
            candidates.add(f"{base} {ARABIC_TO_ROMAN[numeral]}".strip())

    return candidates


class GraphSearcher:

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        communities: Optional[dict] = None,
    ):

        self.graph = graph

        # node -> community_id
        self.communities = communities or {}

        # Precompute normalized match candidates for every node once,
        # instead of recomputing on every search call.
        self._node_candidates: dict[str, set[str]] = {
            node: build_match_candidates(node)
            for node in self.graph.nodes()
        }


    # =====================================================
    # Entity Search
    # =====================================================

    def find_entity(
        self,
        entity_name: str
    ) -> Optional[str]:

        query = entity_name.strip()

        if not query:
            return None

        query_candidates = build_match_candidates(query)
        query_normalized = normalize_text(query)

        # ---------------------------------------------------
        # 1. Exact / acronym / roman-numeral match
        # ---------------------------------------------------
        # Covers: "Grand Theft Auto V" == "grand theft auto v"
        #         "GTA V" / "gta 5" -> "Grand Theft Auto V"
        #         "Final Fantasy VII" <-> "final fantasy 7"

        for node, candidates in self._node_candidates.items():

            if query_candidates & candidates:

                return node


        # ---------------------------------------------------
        # 2. Substring match (normalized, deterministic)
        # ---------------------------------------------------
        # Prefer the shortest matching node name, so a query like
        # "witcher" doesn't arbitrarily resolve to whichever node
        # happens to be first in insertion order.

        substring_matches = [
            node
            for node, candidates in self._node_candidates.items()
            if any(query_normalized in candidate for candidate in candidates)
        ]

        if substring_matches:

            return min(substring_matches, key=len)


        # ---------------------------------------------------
        # 3. Fuzzy match
        # ---------------------------------------------------
        # Try fuzzy matching against both the raw normalized node name
        # and its acronym form, so close misspellings of either style
        # ("wicher" -> "witcher", "gta 5" typo'd as "gta5") still hit.

        lookup: dict[str, str] = {}

        for node, candidates in self._node_candidates.items():

            for candidate in candidates:

                # Keep the shortest node name on collision, for the
                # same determinism reasoning as above.
                if candidate not in lookup or len(node) < len(lookup[candidate]):
                    lookup[candidate] = node

        matches = get_close_matches(
            query_normalized,
            lookup.keys(),
            n=1,
            cutoff=0.55,
        )

        if matches:

            return lookup[matches[0]]


        # ---------------------------------------------------
        # 4. Last resort: best-effort ratio scan
        # ---------------------------------------------------
        # Catches cases difflib's quick filter misses, e.g. short
        # acronym-style queries where get_close_matches' cutoff is
        # too strict relative to string length.

        best_node = None
        best_ratio = 0.0

        for node, candidates in self._node_candidates.items():

            for candidate in candidates:

                ratio = SequenceMatcher(None, query_normalized, candidate).ratio()

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_node = node

        if best_node and best_ratio >= 0.45:

            return best_node


        return None



    # =====================================================
    # Community Retrieval
    # =====================================================

    def get_entity_community(
        self,
        entity: str
    ):

        return self.communities.get(entity)



    def get_community_nodes(
        self,
        community_id
    ):

        return [

            node

            for node, cid
            in self.communities.items()

            if cid == community_id

        ]



    # =====================================================
    # Relation Formatting
    # =====================================================

    def relation_to_sentence(
        self,
        head,
        relation,
        tail,
    ):


        relation_map = {

            "developed_by":
                f"{head} was developed by {tail}.",

            "published_by":
                f"{head} was published by {tail}.",

            "uses_engine":
                f"{head} uses the {tail} game engine.",

            "genre":
                f"{head} belongs to the {tail} genre.",

            "released_in":
                f"{head} was released in {tail}.",

            "has_expansion":
                f"{head} has an expansion called {tail}.",

        }


        return relation_map.get(
            relation,
            f"{head} {relation.replace('_',' ')} {tail}."
        )



    # =====================================================
    # Community Aware Graph Traversal
    # =====================================================

    def retrieve_context(
        self,
        start_entity: str,
        max_depth: int = 2,
        direction="out",
        preferred_relations=None,
    ):


        allowed_nodes = None


        # ---------------------------------
        # Find community
        # ---------------------------------

        community_id = self.get_entity_community(
            start_entity
        )


        if community_id is not None:


            allowed_nodes = set(
                self.get_community_nodes(
                    community_id
                )
            )


            print(
                f"Searching Community {community_id}"
            )


        visited = set()

        queue = deque(
            [
                (
                    start_entity,
                    0
                )
            ]
        )


        facts = []

        seen = set()



        while queue:


            current, depth = queue.popleft()


            if current in visited:

                continue


            visited.add(current)



            if depth >= max_depth:

                continue



            edges = []



            if direction in ("out","both"):


                edges.extend(

                    (
                        current,
                        neighbor,
                        data
                    )

                    for _, neighbor, data

                    in self.graph.out_edges(
                        current,
                        data=True
                    )

                )



            if direction in ("in","both"):


                edges.extend(

                    (
                        source,
                        current,
                        data
                    )

                    for source, _, data

                    in self.graph.in_edges(
                        current,
                        data=True
                    )

                )



            for head, tail, data in edges:



                # Skip nodes outside community

                if allowed_nodes:


                    if (
                        head not in allowed_nodes
                        or
                        tail not in allowed_nodes
                    ):

                        continue



                relation = data.get(
                    "relation",
                    "related_to"
                )



                if (
                    preferred_relations
                    and relation not in preferred_relations
                ):

                    continue



                sentence = self.relation_to_sentence(
                    head,
                    relation,
                    tail
                )



                if sentence not in seen:


                    seen.add(sentence)

                    facts.append(sentence)



                next_node = (
                    tail
                    if head == current
                    else head
                )



                if next_node not in visited:


                    queue.append(
                        (
                            next_node,
                            depth + 1
                        )
                    )



        if not facts:

            return (
                "No relevant graph facts were found."
            )


        return "\n".join(
            f"• {fact}"
            for fact in facts
        )



    # =====================================================
    # Debug
    # =====================================================

    def print_graph(self):

        print(
            "\n========== GRAPH ==========\n"
        )

        print(
            f"Nodes : {self.graph.number_of_nodes()}"
        )

        print(
            f"Edges : {self.graph.number_of_edges()}"
        )

        print(
            "\n===========================\n"
        )