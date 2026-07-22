from pydantic import BaseModel, Field


# ==========================================================
# Request Models
# ==========================================================

class QuestionRequest(BaseModel):
    """
    Request sent from the frontend.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="User's natural language question."
    )


# ==========================================================
# Response Models
# ==========================================================

class QuestionResponse(BaseModel):
    """
    Response returned by GraphRAG.
    """

    question: str

    entity: str

    matched_entity: str

    context: str

    answer: str


class HealthResponse(BaseModel):
    """
    Health check response.
    """

    status: str

    graph_loaded: bool

    nodes: int

    edges: int