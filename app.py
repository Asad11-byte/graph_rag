from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from games_data import GAME_DOCUMENTS

from graph_builder import GraphBuilder
from graph_search import GraphSearcher

from community_detector import CommunityDetector
from community_search import CommunitySearcher

from graph_rag_service import GraphRAGService

from groq_service import GroqService



# ==========================================================
# Initialize GraphRAG System
# ==========================================================

def initialize_graph(app: FastAPI):

    print(
        "\n========== INITIALIZING GRAPH ==========\n"
    )


    # ------------------------------------------------------
    # Groq Service
    # ------------------------------------------------------

    groq_service = GroqService()



    # ------------------------------------------------------
    # Build Knowledge Graph
    # ------------------------------------------------------

    graph_builder = GraphBuilder()


    triples = []


    for index, document in enumerate(
        GAME_DOCUMENTS,
        start=1
    ):

        print(
            f"Processing document {index}..."
        )


        extracted = groq_service.extract_triples(
            document
        )


        print(
            f"✓ Extracted {len(extracted)} triples"
        )


        triples.extend(extracted)



    graph_builder.build(
        triples
    )


    graph_builder.save_json()

    graph_builder.save_graph_html()

    graph_builder.print_statistics()



    # ------------------------------------------------------
    # Community Detection
    # ------------------------------------------------------

    community_detector = CommunityDetector(
        graph_builder.graph
    )


    communities = community_detector.detect()


    community_detector.save_json()



    # ------------------------------------------------------
    # Community Search
    # ------------------------------------------------------

    community_searcher = CommunitySearcher(
        communities
    )



    # ------------------------------------------------------
    # Graph Search
    # ------------------------------------------------------

    graph_searcher = GraphSearcher(
        graph_builder.graph,
        communities
    )



    # ------------------------------------------------------
    # GraphRAG Pipeline
    # ------------------------------------------------------

    graph_rag_service = GraphRAGService(
        graph_searcher,
        community_searcher,
        groq_service,
    )



    # ------------------------------------------------------
    # Global Application State
    # ------------------------------------------------------

    app.state.groq_service = groq_service

    app.state.graph_builder = graph_builder

    app.state.graph_searcher = graph_searcher

    app.state.community_detector = community_detector

    app.state.community_searcher = community_searcher

    app.state.graph_rag_service = graph_rag_service

    app.state.communities = communities



    print(
        "\n✓ Graph initialization completed.\n"
    )



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
# Static
# ==========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)



# ==========================================================
# Templates
# ==========================================================

templates = Jinja2Templates(
    directory="templates",
)



# ==========================================================
# API
# ==========================================================

from api import router

app.include_router(router)