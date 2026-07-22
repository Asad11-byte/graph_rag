import json
from collections import defaultdict
from pathlib import Path

import community as community_louvain
import networkx as nx


class CommunityDetector:
    """
    Detect communities in the Knowledge Graph
    using Louvain algorithm.
    """


    def __init__(
        self,
        graph: nx.MultiDiGraph
    ):

        self.graph = graph

        self.partition = {}

        self.communities = defaultdict(list)


    # =====================================================
    # Detect Communities
    # =====================================================

    def detect(self):

        print(
            "\n========== COMMUNITY DETECTION ==========\n"
        )


        print(
            f"Original Graph : "
            f"{self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )


        if self.graph.number_of_nodes() == 0:

            print("Graph is empty.")

            return {}


        # Convert MultiDiGraph -> Undirected Graph

        undirected = self.graph.to_undirected()


        print(
            f"Undirected Graph : "
            f"{undirected.number_of_nodes()} nodes, "
            f"{undirected.number_of_edges()} edges"
        )


        # Louvain detection

        self.partition = community_louvain.best_partition(
            undirected
        )


        self.communities.clear()


        for node, community_id in self.partition.items():

            self.communities[community_id].append(node)



        print(
            f"\n✓ Detected "
            f"{len(self.communities)} communities"
        )


        self.print_statistics()

        self.print_communities()


        print(
            "\n=========================================\n"
        )


        return self.partition



    # =====================================================
    # Statistics
    # =====================================================

    def print_statistics(self):

        print(
            "\n========== COMMUNITY STATISTICS ==========\n"
        )


        print(
            f"Total Communities : "
            f"{len(self.communities)}"
        )


        for community_id in sorted(
            self.communities.keys()
        ):

            print(
                f"Community {community_id:<3} : "
                f"{len(self.communities[community_id])} nodes"
            )


        print(
            "\n==========================================\n"
        )



    # =====================================================
    # Print Communities
    # =====================================================

    def print_communities(self):

        if not self.communities:

            print(
                "No communities detected."
            )

            return


        print(
            "\n========== COMMUNITIES ==========\n"
        )


        for community_id in sorted(
            self.communities.keys()
        ):

            print(
                f"Community {community_id}"
            )

            print(
                "-" * 30
            )


            for node in sorted(
                self.communities[community_id]
            ):

                print(
                    f"• {node}"
                )


            print()


        print(
            "=================================\n"
        )



    # =====================================================
    # Save JSON
    # =====================================================

    def save_json(
        self,
        output_path="output/communities.json",
    ):

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                self.partition,
                file,
                indent=4,
                ensure_ascii=False,
            )


        print(
            f"✓ Saved communities -> {output_path}"
        )



    # =====================================================
    # Helpers
    # =====================================================

    def get_community(
        self,
        node: str
    ):

        return self.partition.get(node)



    def get_nodes(
        self,
        community_id: int
    ):

        return self.communities.get(
            community_id,
            []
        )



    def get_all_communities(self):

        return dict(
            self.communities
        )