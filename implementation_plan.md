# RAG-Based Customer Support Assistant with LangGraph & HITL

This document outlines the proposed approach for designing and building the retrieval-augmented generation (RAG) system with a graph-based workflow.

## Goal Description

The objective is to design and implement a RAG system that ingests a PDF knowledge base, creates vector embeddings for document retrieval, and uses a graph-based orchestration mechanism (LangGraph) to direct queries. Crucially, the system features a Human-in-the-Loop (HITL) module to escalate unanswerable or complex queries intelligently. The deliverable will be three extensive design documents (HLD, LLD, and Technical Documentation) exported as PDFs, and a fully functioning reference codebase in Python using LangChain, LangGraph, and ChromaDB.

## Phase 1: Design Documentation Generation

I will produce the three required design artifacts as Markdown documents:

1. **High-Level Design (HLD):**
   - System architecture encompassing UI, embedding, vector database, LangGraph orchestration, and HITL.
   - Component-level data flows diagram (rendered using Mermaid.js).
   - Technology choices and scalability considerations.
2. **Low-Level Design (LLD):**
   - Detailed modules, chunking/embedding data structures.
   - Explicit LangGraph logic (Nodes, Edges, State types).
   - Routing/Escalation thresholds and conditions.
3. **Technical Documentation:**
   - Detailed explanations of design choices, trade-offs (e.g. chunk sizes).
   - Complete system workflow and logic for fallback.

After finalizing the markdown format, I will use Python automation (or CLI tools like `mdpdf` / `weasyprint`) to generate high-quality PDF files for your final submission.

## Phase 2: Working Project Implementation

We will proceed with a working Python prototype using state-of-the-art libraries:

### Architecture Setup
- **Embeddings & LLM:** Google Gemini via `langchain-google-genai` (or OpenAI). Let me know which API key you'd prefer to use!
- **Vector Store:** Local `chromadb` instance.
- **Workflow Engine:** `langgraph` for explicit control logic.
- **Interface:** Command Line Interface (CLI) or a lightweight web UI via `gradio`/`streamlit`.

### Core Pipeline modules
#### [NEW] `ingest.py`
Reads a sample PDF, chunks text semantically or recursively, and loads embeddings into ChromaDB.
#### [NEW] `graph_workflow.py`
Defines the `StateGraph` object with nodes: `retrieve_context`, `generate_answer`, `escalate_to_human`, `format_output`.
#### [NEW] `router.py`
Conditional edges logic to classify incoming queries as standard FAQs (directed to RAG) or complex/angry sentiments (diverted to HITL).
#### [NEW] `app.py`
Entry point to run the system and handle the conversation flow.

## Open Questions

> [!IMPORTANT]
> 1. Which LLM provider do you want to use for the working prototype? (e.g., Google Gemini, OpenAI). You will need to provide an API key.
> 2. Do you have a specific PDF in mind to use as a dummy knowledge base, or should I procure a generic customer support policy document?
> 3. For the working project interface, is a rich Command-Line Interface (CLI) sufficient to demonstrate HITL, or do you prefer a lightweight Web App (e.g., Gradio/Streamlit)?

## Verification Plan

### Automated / Unit Tests
- Execute test scripts to assert that simple queries are handled by RAG.
- Feed an "escalation trigger" query and assert the control flow diverts to the HITL node.

### Manual Verification
- Review the generated PDFs for formatting and content depth.
- Run `python app.py` and interact as a user, monitoring LangGraph trace output in the terminal.
