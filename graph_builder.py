import json
from pathlib import Path

import networkx as nx
from pyvis.network import Network

from groq_service import Triple


class GraphBuilder:

    def __init__(self):
        # Directed graph because relationships have direction
        self.graph = nx.MultiDiGraph()

    # --------------------------------------------------------
    # Build Graph
    # --------------------------------------------------------

    def add_triple(self, triple: Triple):
        """Add one knowledge triple to the graph."""

        self.graph.add_node(
            triple.head,
            type="entity"
        )

        self.graph.add_node(
            triple.tail,
            type="entity"
        )

        self.graph.add_edge(
            triple.head,
            triple.tail,
            relation=triple.relation
        )

    def build(self, triples: list[Triple]):
        """Build graph from extracted triples."""

        for triple in triples:
            self.add_triple(triple)

        return self.graph

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def print_statistics(self):

        print("\n========== GRAPH STATISTICS ==========")

        print(f"Nodes : {self.graph.number_of_nodes()}")

        print(f"Edges : {self.graph.number_of_edges()}")

        print("======================================")

    # --------------------------------------------------------
    # Export Triples
    # --------------------------------------------------------

    def save_json(self, output_path="output/triples.json"):

        Path("output").mkdir(exist_ok=True)

        triples = []

        for source, target, data in self.graph.edges(data=True):

            triples.append(
                {
                    "head": source,
                    "relation": data["relation"],
                    "tail": target
                }
            )

        with open(output_path, "w", encoding="utf-8") as file:

            json.dump(
                triples,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"\n✓ Saved JSON -> {output_path}")

    

    # --------------------------------------------------------
    # Interactive Graph (HTML)
    # --------------------------------------------------------

    def save_graph_html(self, output_path="output/graph.html"):

        Path("output").mkdir(exist_ok=True)

        net = Network(
            height="900px",
            width="100%",
            bgcolor="#111827",
            font_color="white",
            directed=True
        )

        colors = {
            "game": "#3b82f6",
            "company": "#22c55e",
            "engine": "#f59e0b",
            "genre": "#a855f7",
            "year": "#6b7280",
            "other": "#ef4444"
        }

        # ----------------------------------------------------
        # Guess node type
        # ----------------------------------------------------

        def node_type(name: str):

            value = name.lower()

            companies = [
                "rockstar",
                "cd projekt",
                "fromsoftware",
                "activision",
                "bandai",
                "supergiant"
            ]

            genres = [
                "rpg",
                "soulslike",
                "action",
                "adventure",
                "roguelike"
            ]

            if value.isdigit():
                return "year"

            if "engine" in value or "rage" in value or "redengine" in value:
                return "engine"

            if any(company in value for company in companies):
                return "company"

            if any(genre in value for genre in genres):
                return "genre"

            return "game"

        # ----------------------------------------------------
        # Nodes
        # ----------------------------------------------------

        for node in self.graph.nodes():

            ntype = node_type(node)

            net.add_node(
                node,
                label=node,
                color=colors.get(ntype, colors["other"]),
                title=f"""
                <b>{node}</b><br>
                Type: {ntype.title()}
                """
            )

        # ----------------------------------------------------
        # Edges
        # ----------------------------------------------------

        for source, target, data in self.graph.edges(data=True):

            net.add_edge(
                source,
                target,
                label=data["relation"],
                title=data["relation"],
                arrows="to"
            )

        # ----------------------------------------------------
        # Physics
        # ----------------------------------------------------

        net.set_options("""
        var options = {
          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          },

          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -12000,
              "springLength": 180,
              "springConstant": 0.04
            },
            "stabilization": {
              "iterations": 300
            }
          },

          "nodes": {
            "shape": "dot",
            "size": 22,
            "font": {
              "size": 18
            }
          },

          "edges": {
            "smooth": true,
            "font": {
              "size": 13,
              "align": "middle"
            },
            "arrows": {
              "to": {
                "enabled": true
              }
            }
          }
        }
        """)

        net.show(output_path, notebook=False)

        print(f"✓ Saved Interactive Graph -> {output_path}")