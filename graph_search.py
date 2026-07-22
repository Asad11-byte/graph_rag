from collections import deque
from difflib import get_close_matches
from typing import Optional

import networkx as nx


class GraphSearcher:

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        communities: Optional[dict] = None,
    ):

        self.graph = graph

        # node -> community_id
        self.communities = communities or {}


    # =====================================================
    # Entity Search
    # =====================================================

    def find_entity(
        self,
        entity_name: str
    ) -> Optional[str]:

        query = entity_name.strip().lower()


        # Exact match

        for node in self.graph.nodes():

            if node.lower() == query:

                return node



        # Partial match

        for node in self.graph.nodes():

            if query in node.lower():

                return node



        # Fuzzy match

        lookup = {
            node.lower(): node
            for node in self.graph.nodes()
        }


        matches = get_close_matches(
            query,
            lookup.keys(),
            n=1,
            cutoff=0.60,
        )


        if matches:

            return lookup[matches[0]]


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