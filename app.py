import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from community_detector import CommunityDetector
from community_search import CommunitySearcher
from games_data import GAME_DOCUMENTS
from graph_builder import GraphBuilder
from graph_rag_service import GraphRAGService
from graph_search import GraphSearcher
from groq_service import GroqService

# Absolute path resolution for Vercel Serverless runtime
BASE_DIR = Path(__file__).resolve().parent


# ==========================================================
# Initialize GraphRAG System
# ==========================================================

def initialize_graph(app: FastAPI):

    # Groq Service
    groq_service = GroqService()

    # Build Knowledge Graph
    graph_builder = GraphBuilder()

    triples = []

    for index, document in enumerate(GAME_DOCUMENTS, start=1):
        print(f"Processing document {index}...")
        extracted = groq_service.extract_triples(document)
        print(f"✓ Extracted {len(extracted)} triples")
        triples.extend(extracted)

    graph_builder.build(triples)
    graph_builder.save_json()
    graph_builder.save_graph_html()
    graph_builder.print_statistics()

    # Community Detection
    community_detector = CommunityDetector(graph_builder.graph)
    communities = community_detector.detect()
    community_detector.save_json()

    # Community Search
    community_searcher = CommunitySearcher(communities)

    # Graph Search
    graph_searcher = GraphSearcher(graph_builder.graph, communities)

    # GraphRAG Pipeline
    graph_rag_service = GraphRAGService(
        graph_searcher,
        community_searcher,
        groq_service,
    )

    # Global Application State
    app.state.groq_service = groq_service
    app.state.graph_builder = graph_builder
    app.state.graph_searcher = graph_searcher
    app.state.community_detector = community_detector
    app.state.community_searcher = community_searcher
    app.state.graph_rag_service = graph_rag_service
    app.state.communities = communities

    print("\n✓ Graph initialization completed.\n")


# ==========================================================
# Lifespan
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_graph(app)

    yield

    print(
        "\nApplication shutting down...\n"
    )


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="GraphRAG Game Assistant",
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================================
# Static Files
# ==========================================================

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static",
    )


# ==========================================================
# Templates
# ==========================================================

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"),
)


# ==========================================================
# API Routes
# ==========================================================

from api import router

app.include_router(router)