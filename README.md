# 🎮 GraphRAG Game Assistant

A **Graph Retrieval-Augmented Generation (GraphRAG)** application that automatically builds a knowledge graph from game-related documents using a Large Language Model (LLM), detects semantic communities, retrieves relevant graph knowledge, and generates accurate answers using Groq.

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
* [Running the Application](#running-the-application)
* [API Endpoints](#api-endpoints)
* [GraphRAG Workflow](#graphrag-workflow)
* [Knowledge Graph Construction](#knowledge-graph-construction)
* [Community Detection](#community-detection)
* [Graph Retrieval](#graph-retrieval)
* [Graph Visualization](#graph-visualization)
* [Example Query](#example-query)
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

---

# Features

* Automatic Knowledge Graph construction
* LLM-based triple extraction
* Entity extraction using Groq
* Knowledge Graph built with NetworkX
* Louvain community detection
* Community-aware graph traversal
* Natural language graph retrieval
* FastAPI REST API
* Interactive graph visualization
* JSON graph export
* Community export
* Clean modular architecture

---

# Architecture

```text
                Game Documents
                       │
                       ▼
             Groq Triple Extraction
                       │
                       ▼
              Knowledge Triples
                       │
                       ▼
        NetworkX MultiDiGraph Builder
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
Groq
(Triple Extraction)
    │
    ▼
Knowledge Graph
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

| Component           | Technology     |
| ------------------- | -------------- |
| Backend             | FastAPI        |
| LLM                 | Groq           |
| Graph               | NetworkX       |
| Community Detection | python-louvain |
| Validation          | Pydantic       |
| Templates           | Jinja2         |
| Graph Visualization | PyVis          |
| Environment         | python-dotenv  |

---

# Project Structure

```text
graph_rag/
│
├── api.py
├── app.py
├── community_detector.py
├── community_search.py
├── graph_builder.py
├── graph_rag_service.py
├── graph_search.py
├── groq_service.py
├── games_data.py
├── prompts.py
├── models.py
│
├── templates/
│   └── index.html
│
├── static/
│
├── output/
│   ├── graph.html
│   ├── triples.json
│   └── communities.json
│
└── README.md
```

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

Game descriptions are loaded from `games_data.py`.

---

## Step 2

Triple Extraction

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

Graph Construction

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

---

## Step 4

Community Detection

The graph is converted into an undirected graph.

The Louvain algorithm groups related nodes into communities.

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

Entity Extraction

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

Entity Matching

The extracted entity is matched against graph nodes using

* Exact match
* Partial match
* Fuzzy match

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
* Graph node matching (exact, partial, fuzzy).
* Community lookup.
* Breadth-First Search (BFS).
* Natural-language conversion of graph relations.

This design retrieves graph facts directly rather than performing vector similarity search.

---

# Graph Visualization

The project exports

```
output/graph.html
```

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
* Incremental graph updates
* Streaming responses

These are natural future enhancements.

---

# Future Improvements

* Hybrid graph + vector retrieval
* Community summarization
* Retrieval ranking
* Graph embeddings
* Neo4j support
* Incremental graph updates
* Multi-document ingestion
* Streaming API responses
* Authentication
* Docker deployment
* Automated testing

---

# License

This project is provided for educational and research purposes.

Feel free to modify and extend it for your own learning or applications.
