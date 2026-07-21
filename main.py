from games_data import GAME_DOCUMENTS
from graph_builder import GraphBuilder
from groq_service import GroqService

groq = GroqService()

builder = GraphBuilder()

all_triples = []

print("\nExtracting knowledge...\n")

for i, document in enumerate(GAME_DOCUMENTS, start=1):

    print(f"Processing document {i}...")

    triples = groq.extract_triples(document)

    all_triples.extend(triples)

builder.build(all_triples)

builder.print_statistics()

builder.save_json()

builder.save_graph_image() 
builder.save_graph_html()
