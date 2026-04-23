# RAG-Based Customer Support Assistant 🤖

An advanced Retrieval-Augmented Generation (RAG) agentic workflow designed for customer support systems. Built utilizing **LangGraph** for explicit state orchestration and control logic, with a native **Human-In-The-Loop (HITL)** failover mechanism.

## Overview
Unlike generic linear RAG pipelines, this system operates dynamically. It utilizes a zero-shot Intent Classifier at the beginning of the Graph Node traversal. If a user asks a trivial policy question, the query is routed to a Local Vector Store (ChromaDB) to synthesize an answer via Groq's high-speed inference. However, if the system detects intense frustration, complex billing queries, or legal threats within the prompt, it instantly freezes automated generation, emits an alert via the interface, and securely pipes control directly to a Human Agent to step in!

## Tech Stack
- **Orchestration:** LangGraph & LangChain
- **LLM / Generation:** Groq API (`llama-3.1-8b-instant`)
- **Vector Database:** ChromaDB (Local Persist)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Local - Zero API cost)
- **Interface:** Gradio (Web Dashboard UI)

## Features
- **Semantic Chunking:** Leverages recursive character splitting natively overlapping semantic concepts across the knowledge base.
- **Agentic Routing:** Evaluates User Intent prior to allocating Retrieval Compute.
- **Stateful Memory Checkpointing:** Maintains conversation thread histories across the graph using LangGraph MemorySavers.
- **Human in the Loop:** A built-in system interrupt enabling supervisors to inject manual overrides into the LLM conversation stream.

## Setup Instructions

### 1. Configure the Environment
Provide your Groq API Key by creating a `.env` file in the root project folder:
```env
GROQ_API_KEY=gsk_your_api_key_here
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Execution Pipeline
Run the following scripts in order to build the backend and ingest the mock PDF company policies:
```powershell
# Generate the mock corporate PDF Policy Document
python mock_data.py

# Ingest, embed, and map the PDF into ChromaDB
python ingest.py

# Spin up the Gradio user interface on localhost
python app.py
```

*Or just execute `.\run.bat` on Windows for a one-click deployment!*

## Deliverables Note
The `HLD.md`, `LLD.md`, and `Technical_Documentation.md` artifacts define the architectural blueprints of this implementation and are optimized for Markdown-to-PDF export.
