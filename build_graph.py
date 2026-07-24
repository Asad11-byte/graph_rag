"""
Run this LOCALLY (not on Vercel) whenever GAME_DOCUMENTS changes:

    python build_graph.py

It calls Groq once to extract triples, builds the graph, and writes
data/triples.json (+ data/graph.html for the visualization). Commit
both files to the repo — app.py loads them at startup instead of
rebuilding the graph on every cold start.
"""

from pathlib import Path

from games_data import GAME_DOCUMENTS
from graph_builder import GraphBuilder
from groq_service import GroqService

OUTPUT_DIR = Path("data")


def main():
    groq_service = GroqService()
    graph_builder = GraphBuilder()

    triples = []

    for index, document in enumerate(GAME_DOCUMENTS, start=1):
        print(f"Processing document {index}/{len(GAME_DOCUMENTS)}...")
        extracted = groq_service.extract_triples(document)
        print(f"✓ Extracted {len(extracted)} triples")
        triples.extend(extracted)

    graph_builder.build(triples)
    graph_builder.print_statistics()

    graph_builder.save_json(OUTPUT_DIR / "triples.json")
    graph_builder.save_graph_html(OUTPUT_DIR / "graph.html")

    print(f"\n✓ Done. Commit {OUTPUT_DIR}/triples.json and {OUTPUT_DIR}/graph.html to your repo.\n")


if __name__ == "__main__":
    main()