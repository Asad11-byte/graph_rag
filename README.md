# 🎮 GraphRAG Game Assistant

A **Graph Retrieval-Augmented Generation (GraphRAG)** application that automatically builds a knowledge graph from documents using a Large Language Model (LLM), detects semantic communities, retrieves relevant graph knowledge, and generates accurate answers using Groq.

Although the current dataset is about video games, the pipeline is **domain-agnostic** — see [Changing the Data / Domain](#changing-the-data--domain) to point it at movies, books, companies, or anything else.

---

## 🔗 Live Demo

> **[your-project-name.vercel.app](https://graph-4r7j3kgqy-asad11-bytes-projects.vercel.app/)**

*(Replace this link once deployed. See [Deployment](#deployment) below.)*

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Architecture](#architecture)
* [Project Pipeline](#project-pipeline)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Installation](#installation)
* [Environment Variables](#environment-variables)
* [Building the Knowledge Graph](#building-the-knowledge-graph)
* [Running the Application](#running-the-application)
* [Deployment](#deployment)
* [Changing the Data / Domain](#changing-the-data--domain)
* [API Endpoints](#api-endpoints)
* [GraphRAG Workflow](#graphrag-workflow)
* [Knowledge Graph Construction](#knowledge-graph-construction)
* [Community Detection](#community-detection)
* [Graph Retrieval](#graph-retrieval)
* [Entity Matching](#entity-matching)
* [Graph Visualization](#graph-visualization)
* [Example Query](#example-query)
* [Current Limitations](#current-limitations)
* [Future Improvements](#future-improvements)
* [License](#license)

---

# Overview

GraphRAG Game Assistant demonstrates how a Large Language Model can be combined with a Knowledge Graph to answer questions about video games.

Instead of searching raw text, the system:

1. Reads documents.
2. Extracts structured knowledge triples.
3. Builds a Knowledge Graph.
4. Detects graph communities.
5. Retrieves graph facts relevant to a question.
6. Uses Groq to generate a grounded answer.

The project focuses on **graph-based retrieval** rather than traditional vector similarity search.

> **Note on architecture:** Triple extraction (the Groq call over all source documents) is a **one-time, offline build step**, not something that runs on every server start or every request. The API loads a precomputed graph at startup. This keeps the app fast and cheap to run, and is required for serverless platforms like Vercel where request-time LLM extraction over every document would be far too slow. See [Building the Knowledge Graph](#building-the-knowledge-graph).

---

# Features

* Automatic Knowledge Graph construction (offline build step)
* LLM-based triple extraction
* Entity extraction using Groq
* Knowledge Graph built with NetworkX
* Louvain community detection
* Community-aware graph traversal
* Normalized, acronym- and roman-numeral-aware entity matching (e.g. `"GTA V"` ↔ `"Grand Theft Auto 5"`)
* Natural language graph retrieval
* FastAPI REST API
* Interactive graph visualization
* JSON graph export
* Community export
* Clean modular architecture
* Deployable to Vercel (serverless)

---

# Architecture

```text
                Game Documents
                       │
                       ▼
             Groq Triple Extraction        ← offline, build_graph.py
                       │
                       ▼
              Knowledge Triples
                       │
                       ▼
        NetworkX MultiDiGraph Builder
                       │
                       ▼
              data/triples.json            ← committed to repo
                       │
   ═══════════════════ runtime starts here ═══════════════════
                       │
                       ▼
              GraphBuilder.from_json()
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
Community Detection            Graph Visualization
        │
        ▼
Community Search
        │
        ▼
Graph Search
        │
        ▼
GraphRAG Service
        │
 ┌──────┼───────────────────────┐
 ▼      ▼                       ▼
Entity  Graph Retrieval     Groq Answer
Extraction
        │
        ▼
     FastAPI API
```

---

# Project Pipeline

```text
Documents
    │
    ▼
Groq (Triple Extraction)      ← run once locally via build_graph.py
    │
    ▼
data/triples.json             ← committed, loaded at startup
    │
    ▼
Knowledge Graph (in memory)
    │
    ▼
Community Detection
    │
    ▼
Entity Extraction
    │
    ▼
Community Lookup
    │
    ▼
Graph Traversal
    │
    ▼
Context Creation
    │
    ▼
Groq Answer Generation
```

---

# Technology Stack

| Component            | Technology     |
| --------------------- | -------------- |
| Backend               | FastAPI        |
| LLM                    | Groq           |
| Graph                  | NetworkX       |
| Community Detection    | python-louvain |
| Validation              | Pydantic       |
| Templates                | Jinja2         |
| Graph Visualization      | PyVis          |
| Environment                | python-dotenv  |
| Deployment                   | Vercel (serverless, Python runtime) |

---

# Project Structure

```text
graph_rag/
│
├── api.py
├── app.py                  # FastAPI app; loads precomputed graph at startup
├── build_graph.py          # Run locally to (re)generate the graph data
├── community_detector.py
├── community_search.py
├── graph_builder.py
├── graph_rag_service.py
├── graph_search.py
├── groq_service.py
├── games_data.py           # ← source documents; swap this to change domain
├── prompts.py
├── models.py
├── vercel.json
├── requirements.txt
│
├── templates/
│   └── index.html
│
├── static/
│
├── data/                   # Committed to git — the "built" graph
│   ├── triples.json
│   └── graph.html
│
└── README.md
```

> `data/` replaces the old `output/` folder as the source the app reads from. `output/` (if present) is now only used for scratch/local regeneration and is safe to `.gitignore`.

---

# Installation

Clone the repository

```bash
git clone <repository-url>
cd graph_rag
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key
```

`.env` is for **local development only**. When deploying (e.g. to Vercel), set `GROQ_API_KEY` in the platform's environment variable settings instead — `.env` files are not deployed.

---

# Building the Knowledge Graph

The graph is **not** built automatically when the server starts. Build it once, locally, whenever `games_data.py` changes:

```bash
python build_graph.py
```

This will:

1. Call Groq to extract triples from every document in `games_data.py`.
2. Build the NetworkX graph.
3. Write `data/triples.json` (the data the app loads at runtime).
4. Write `data/graph.html` (the interactive visualization served at `/graph`).

After running it, commit the output:

```bash
git add data/triples.json data/graph.html
git commit -m "Rebuild knowledge graph"
```

`app.py` will refuse to start (raising a clear error) if `data/triples.json` is missing — this is intentional, to avoid silently falling back to a slow, request-time rebuild.

---

# Running the Application

```bash
uvicorn app:app --reload
```

Default server

```
http://127.0.0.1:8000
```

---

# Deployment

This project is designed to run as a serverless Python function on **Vercel**.

Key points for a working deployment:

* `data/triples.json` and `data/graph.html` must be committed to the repo — they are read at startup instead of being generated on the server.
* Set `GROQ_API_KEY` under **Vercel Dashboard → Project → Settings → Environment Variables**.
* `vercel.json` declares `app.py` as the entrypoint and sets `maxDuration` for the function.
* Static assets (`static/`) can optionally be moved to a `public/` directory so Vercel's CDN serves them directly instead of routing every asset request through the Python function.
* The Hobby plan gives you up to 300s per function invocation with Fluid Compute; Pro/Enterprise up to ~800s. Adjust `maxDuration` in `vercel.json` if your `/ask` endpoint's Groq calls are slow.

Minimal deploy steps:

```bash
npm install -g vercel
vercel deploy
```

Or connect the GitHub repo directly in the Vercel dashboard for automatic deployments on push.

---

# Changing the Data / Domain

The GraphRAG pipeline itself has no game-specific logic — everything domain-specific lives in **`games_data.py`** (the source documents) and, loosely, in the labels used for visualization coloring in `graph_builder.py`. To repurpose this project for a different domain (movies, companies, books, historical events, your own product docs, etc.):

### 1. Replace the source documents

Open `games_data.py` and replace `GAME_DOCUMENTS` with your own list of text documents/descriptions. Each entry should be a self-contained piece of text describing entities and their relationships — the LLM extracts triples from each one independently.

```python
# games_data.py  →  rename or repurpose as you like, e.g. movies_data.py

DOCUMENTS = [
    "The Matrix (1999) was directed by the Wachowskis and stars Keanu Reeves...",
    "Inception (2010) was directed by Christopher Nolan and produced by Warner Bros...",
    # ...
]
```

If you rename the file/variable, update the two places that import it:

* `build_graph.py` — `from games_data import GAME_DOCUMENTS`

### 2. (Optional) Adjust the extraction prompt

`prompts.py` likely contains the instructions Groq uses to extract triples (relation types, formatting rules). If your new domain has different natural relation types (e.g. `directed_by`, `starring`, `produced_by` instead of `developed_by`, `uses_engine`), update the prompt so the LLM extracts relations that make sense for your data. This isn't strictly required — the pipeline works with whatever relation strings the model returns — but tailoring it improves extraction quality.

### 3. (Optional) Adjust visualization node coloring

`graph_builder.py`'s `save_graph_html()` has a `node_type()` helper that guesses node categories (`game`, `company`, `engine`, `genre`, `year`) from keyword lists, purely for coloring the interactive graph. For a different domain, update the `companies` / `genres` keyword lists (or the categories entirely) to match your entity types. This is cosmetic only — it doesn't affect retrieval or answers.

### 4. Rebuild the graph

```bash
python build_graph.py
```

This regenerates `data/triples.json` and `data/graph.html` from your new documents.

### 5. Update user-facing copy (optional)

`templates/index.html`, the FastAPI `title` in `app.py`, and this README's examples reference "games" — update wording there if you want the UI/docs to reflect the new domain. None of this affects functionality.

### 6. Commit and redeploy

```bash
git add data/triples.json data/graph.html games_data.py
git commit -m "Switch dataset to <new domain>"
git push
```

That's the entire process — the graph construction, community detection, entity matching (including the acronym/roman-numeral normalization), and retrieval logic are all domain-agnostic and require no code changes.

---

# API Endpoints

## Home

```
GET /
```

Returns the web interface.

---

## Ask a Question

```
POST /ask
```

Example

```json
{
    "question": "What engine does Cyberpunk 2077 use?"
}
```

Example response

```json
{
    "question": "...",
    "entity": "Cyberpunk 2077",
    "matched_entity": "Cyberpunk 2077",
    "context": "...",
    "answer": "Cyberpunk 2077 uses REDengine 4."
}
```

---

## Health

```
GET /health
```

Returns graph statistics.

---

## Graph Visualization

```
GET /graph
```

Opens the interactive graph.

---

# GraphRAG Workflow

## Step 1

Document Loading

Documents are loaded from `games_data.py` (or your renamed equivalent).

---

## Step 2

Triple Extraction *(offline, via `build_graph.py`)*

Groq extracts structured triples.

Example

```text
Cyberpunk 2077
      │
developed_by
      │
CD Projekt Red
```

Another example

```text
Cyberpunk 2077
      │
uses_engine
      │
REDengine 4
```

---

## Step 3

Graph Construction *(offline, via `build_graph.py`)*

Each triple becomes

* a head node
* a relation edge
* a tail node

Example

```text
Cyberpunk 2077
        │
 developed_by
        │
CD Projekt Red
```

The resulting graph is saved to `data/triples.json`.

---

## Step 4

Community Detection *(runtime, on app startup — fast, local, no LLM calls)*

The graph is loaded from `data/triples.json`, converted into an undirected graph, and the Louvain algorithm groups related nodes into communities.

Example

```
Community 0

Cyberpunk 2077
REDengine 4
2020
Phantom Liberty
```

---

## Step 5

Entity Extraction *(runtime, per request)*

When a user asks

```
Who developed Cyberpunk 2077?
```

Groq extracts

```
Cyberpunk 2077
```

---

## Step 6

Entity Matching *(runtime, per request)*

The extracted entity is matched against graph nodes. See [Entity Matching](#entity-matching) for details.

---

## Step 7

Community Lookup

The matched entity's community is identified.

Example

```
Cyberpunk 2077

↓

Community 0
```

---

## Step 8

Graph Retrieval

The graph is traversed using Breadth-First Search (BFS).

Retrieved facts are converted into readable sentences.

Example

```
Cyberpunk 2077 was developed by CD Projekt Red.

Cyberpunk 2077 uses the REDengine 4 game engine.

Cyberpunk 2077 has an expansion called Phantom Liberty.
```

---

## Step 9

Answer Generation

The retrieved graph context and the user's question are sent to Groq.

The model generates a final answer grounded in the retrieved graph facts.

---

# Knowledge Graph Construction

The project stores knowledge as

```
Head

Relation

Tail
```

Example

```
Cyberpunk 2077

uses_engine

REDengine 4
```

Internally

```
Node
Edge
Node
```

---

# Community Detection

The project uses the **Louvain algorithm**.

Purpose

* Discover clusters of related entities.
* Restrict retrieval to relevant graph regions.
* Reduce irrelevant graph exploration.

Current implementation performs **community-filtered graph traversal**, meaning traversal remains within the detected community whenever a community is available.

---

# Graph Retrieval

The retrieval process currently combines:

* Entity extraction with the LLM.
* Normalized graph node matching (exact, acronym/roman-numeral aware, substring, fuzzy).
* Community lookup.
* Breadth-First Search (BFS).
* Natural-language conversion of graph relations.

This design retrieves graph facts directly rather than performing vector similarity search.

---

# Entity Matching

`GraphSearcher.find_entity()` resolves a user/LLM-extracted entity string to an actual graph node using, in order:

1. **Exact / acronym / roman-numeral match** — text is normalized (lowercased, punctuation stripped) and compared against precomputed equivalents for every node, including acronym forms (`"Grand Theft Auto V"` → `"gta v"` / `"gta 5"`) and roman-numeral ↔ digit swaps (`"Final Fantasy VII"` ↔ `"final fantasy 7"`).
2. **Substring match** — normalized substring containment, deterministically resolving to the shortest matching node name.
3. **Fuzzy match** — `difflib.get_close_matches` over normalized and acronym forms.
4. **Best-effort ratio scan** — a final fallback for near-misses the quicker fuzzy pass discards.

This means queries like `"gta v"`, `"GTA 5"`, and `"Grand Theft Auto V"` all resolve to the same node without any manual alias list.

---

# Graph Visualization

The project exports

```
data/graph.html
```

(generated once by `build_graph.py`, served directly at `/graph` — not regenerated per request)

Features

* Interactive nodes
* Relationship edges
* Zoom
* Drag
* Physics simulation

---

# Example Query

Question

```
What engine does Cyberpunk 2077 use?
```

Retrieved Context

```
Cyberpunk 2077 was developed by CD Projekt Red.

Cyberpunk 2077 uses the REDengine 4 game engine.

Cyberpunk 2077 has an expansion called Phantom Liberty.
```

Answer

```
Cyberpunk 2077 uses the REDengine 4 game engine.
```

---

# Current Limitations

This project demonstrates a GraphRAG workflow but is intentionally lightweight.

Compared with large-scale GraphRAG systems, it currently does **not** include:

* Graph database storage (e.g., Neo4j)
* Community summarization
* Hierarchical community organization
* Retrieval ranking of graph facts
* Hybrid vector + graph retrieval
* Incremental graph updates (adding a single new document still requires rerunning `build_graph.py` over the whole dataset)
* Streaming responses

These are natural future enhancements.

---

# Future Improvements

* Hybrid graph + vector retrieval
* Community summarization
* Retrieval ranking
* Graph embeddings
* Neo4j support
* Incremental graph updates (append-only triple extraction instead of full rebuilds)
* Multi-document ingestion
* Streaming API responses
* Authentication
* Docker deployment
* Automated testing

---

# License

This project is provided for educational and research purposes.

Feel free to modify and extend it for your own learning or applications.