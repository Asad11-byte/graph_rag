GRAPH_EXTRACTION_PROMPT = """
You are an expert knowledge graph extraction system.

Extract every factual relationship from the text.

Return ONLY valid JSON.

Format:

[
  {{
    "head": "...",
    "relation": "...",
    "tail": "..."
  }}
]

Allowed relations:

developed_by

published_by

uses_engine

genre

released_in

has_expansion

Do not explain anything.

Return only JSON.

TEXT:

{text}
"""