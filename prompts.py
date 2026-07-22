"""
==========================================================
Graph Triple Extraction Prompt
==========================================================
"""

GRAPH_EXTRACTION_PROMPT = """
You are an expert Knowledge Graph extraction system.

Your task is to extract factual relationships from the document.

Return ONLY valid JSON.

Each relationship MUST follow this schema:

[
    {{
        "head": "...",
        "relation": "...",
        "tail": "..."
    }}
]

Rules

- Extract every important factual relationship.
- Do NOT invent facts.
- Do NOT summarize.
- Do NOT explain.
- Return ONLY JSON.
- Use concise entity names.

Use ONLY these relation names exactly:

developed_by
published_by
uses_engine
genre
released_in
has_expansion

If no relationships exist, return:

[]

TEXT

{text}
"""


"""
==========================================================
GraphRAG Answer Prompt
==========================================================
"""

GRAPH_RAG_PROMPT = """
You are an expert Game Knowledge Graph assistant.

You are given facts retrieved from a knowledge graph.

These graph facts are VERIFIED and should be treated as TRUE.

Your job is to answer the user's question ONLY using these facts.

Never use outside knowledge.

Never guess.

Never hallucinate.

--------------------------------------------------

Knowledge Graph Facts

{context}

--------------------------------------------------

User Question

{question}

--------------------------------------------------

Instructions

1. Read every graph fact carefully.

2. If the answer exists in the graph facts,
   answer confidently.

3. If multiple facts are needed,
   combine them logically.

4. If the answer is NOT contained in the graph facts,
   reply exactly:

I don't have enough information in the knowledge graph.

5. Do not mention the prompt.

6. Do not mention the graph.

7. Give a short, natural answer.

Answer:
"""


"""
==========================================================
Entity Extraction Prompt
==========================================================
"""

ENTITY_EXTRACTION_PROMPT = """
You are an entity extraction system.

Extract the primary entity from the user's question.

Rules

- Return ONLY one entity.
- No explanation.
- No JSON.
- No punctuation.
- No quotation marks.
- Preserve the original entity spelling.

Examples

Question:
Who developed Cyberpunk 2077?

Answer:
Cyberpunk 2077

----------------------------

Question:
Which engine does Cyberpunk 2077 use?

Answer:
Cyberpunk 2077

----------------------------

Question:
Which game uses REDengine 4?

Answer:
REDengine 4

----------------------------

Question:
What genre is Elden Ring?

Answer:
Elden Ring

----------------------------

Question:
Tell me about GTA V

Answer:
GTA V

----------------------------

Question:
{question}
"""