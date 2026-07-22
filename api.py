from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from models import (
    HealthResponse,
    QuestionRequest,
    QuestionResponse,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="templates",
)


# ==========================================================
# Home
# ==========================================================

@router.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# ==========================================================
# Ask GraphRAG
# ==========================================================

@router.post(
    "/ask",
    response_model=QuestionResponse,
)
async def ask_question(
    request: Request,
    payload: QuestionRequest,
):
    """
    Main GraphRAG endpoint.

    Pipeline:
        User Question
            ↓
        GraphRAGService
            ↓
        JSON Response
    """

    graph_rag_service = getattr(
        request.app.state,
        "graph_rag_service",
        None,
    )

    if graph_rag_service is None:

        raise HTTPException(
            status_code=500,
            detail="GraphRAG service is not initialized.",
        )

    result = graph_rag_service.answer(
        payload.question.strip()
    )

    if isinstance(result, str):

        raise HTTPException(
            status_code=404,
            detail=result,
        )

    return QuestionResponse(
        question=result["question"],
        entity=result["entity"],
        matched_entity=result["matched_entity"],
        context=result["context"],
        answer=result["answer"],
    )


# ==========================================================
# Health Check
# ==========================================================

@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health(
    request: Request,
):

    builder = getattr(
        request.app.state,
        "graph_builder",
        None,
    )

    loaded = builder is not None

    nodes = (
        builder.graph.number_of_nodes()
        if loaded
        else 0
    )

    edges = (
        builder.graph.number_of_edges()
        if loaded
        else 0
    )

    return HealthResponse(
        status="healthy",
        graph_loaded=loaded,
        nodes=nodes,
        edges=edges,
    )


# ==========================================================
# Interactive Graph
# ==========================================================

@router.get("/graph")
async def graph():

    file = Path(
        "output/graph.html"
    )

    if not file.exists():

        raise HTTPException(
            status_code=404,
            detail="Graph visualization not found.",
        )

    return FileResponse(file)