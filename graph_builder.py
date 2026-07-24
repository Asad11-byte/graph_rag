import json
import os
from pathlib import Path

import networkx as nx

from groq_service import Triple

# Set dynamic output path based on Vercel serverless environment.
# Note: /tmp is writable but ephemeral — it does NOT persist across cold
# starts or across concurrent instances. It's fine as a scratch space
# (e.g. for save_json/save_graph_html when you deliberately want to
# regenerate output during local development), but it must never be
# relied on as the source of truth at request time in production.
IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_OUTPUT_DIR = Path("/tmp/output") if IS_VERCEL else Path("output")


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
    # Load From Precomputed JSON (fast path, no LLM calls)
    # --------------------------------------------------------

    @classmethod
    def from_json(cls, input_path: str | Path) -> "GraphBuilder":
        """
        Reconstruct a graph from a previously saved triples JSON file.

        This is the path that should run at application startup /
        request time (e.g. in app.py's lifespan). It does no network
        I/O and no disk writes — just reads a bundled data file and
        rebuilds the in-memory graph, so it's fast and safe to run on
        every cold start.

        The JSON file itself should be produced offline by calling
        save_json() from a local build script and committing the
        result to the repo.
        """
        target_path = Path(input_path)

        if not target_path.exists():
            raise FileNotFoundError(
                f"Precomputed graph data not found at {target_path}. "
                "Generate it locally (e.g. via build_graph.py) and commit it."
            )

        with open(target_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        builder = cls()

        triples = [
            Triple(
                head=item["head"],
                relation=item["relation"],
                tail=item["tail"],
            )
            for item in data
        ]

        builder.build(triples)

        return builder

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

    def save_json(self, output_path: str | Path | None = None):
        """
        Save extracted triples to a JSON file.

        Intended to be run offline (e.g. from build_graph.py, on your
        own machine or a CI job) — NOT from request-handling code on
        Vercel. The output of this call is what from_json() reads
        back at runtime, so commit it to the repo after regenerating.
        """
        if output_path is None:
            target_path = DEFAULT_OUTPUT_DIR / "triples.json"
        else:
            target_path = Path(output_path)

        # Ensure target directory exists in writable location
        target_path.parent.mkdir(parents=True, exist_ok=True)

        triples = []

        for source, target, data in self.graph.edges(data=True):

            triples.append(
                {
                    "head": source,
                    "relation": data["relation"],
                    "tail": target
                }
            )

        with open(target_path, "w", encoding="utf-8") as file:

            json.dump(
                triples,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"\n✓ Saved JSON -> {target_path}")

    # --------------------------------------------------------
    # Interactive Graph (HTML)
    # --------------------------------------------------------

    def save_graph_html(self, output_path: str | Path | None = None):
        """
        Save PyVis interactive graph HTML.

        Also intended to run offline via build_graph.py — pyvis is a
        heavy dependency and rendering is unnecessary request-time
        work. Commit the generated HTML (e.g. to data/graph.html) and
        serve it as a static file from app.py instead of regenerating
        it on every request.
        """
        # Imported here so pyvis is only required when actually
        # building/regenerating the visualization, not at app runtime.
        from pyvis.network import Network

        if output_path is None:
            target_path = DEFAULT_OUTPUT_DIR / "graph.html"
        else:
            target_path = Path(output_path)

        # Ensure target directory exists in writable location
        target_path.parent.mkdir(parents=True, exist_ok=True)

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

        net.show(str(target_path), notebook=False)

        print(f"✓ Saved Interactive Graph -> {target_path}")