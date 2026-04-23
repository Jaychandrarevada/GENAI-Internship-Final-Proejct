# Low-Level Design (LLD)
## RAG-Based Customer Support Assistant (with LangGraph & HITL)

### 1. Module-Level Design

- **Document Processing Module:** Integrates `PyPDFLoader` to parse text and strip non-ASCII noisy artifacts.
- **Chunking Module:** Utilizes `RecursiveCharacterTextSplitter`. Chunking parameters defined as `chunk_size = 1000` and `chunk_overlap = 150` characters.
- **Embedding Module:** Instantiates the LLM provider's chosen embedding model. Takes in a string and outputs a high-dimensional vector.
- **Vector Storage Module:** Managed by Chroma DB Client (`PersistentClient`). Uses collection names to store document namespace. Provides a `similarity_search(query)` interface.
- **Retrieval Module:** Acts as middleware wrapping ChromaDB, taking the user query, applying the embedding model, fetching top 5 chunks (`k=5`), and joining strings together into a `context` variable.
- **Query Processing Module:** The core Router schema. Takes query input, issues a zero-shot prompt to an LLM evaluator to classify intent into explicitly ENUM options.
- **Graph Execution Module:** Implements `langgraph.graph.StateGraph`. Compiles nodes (Python functions) and maps branching logic explicitly. Features memory preservation tracking historical graph state.
- **HITL Module:** Pauses graph execution using an interrupt. Captures STDIN via the terminal, modifies the graph's `State` to append a human string, and triggers resuming execution.

### 2. Data Structures

**Document Representation:**
```json
{
  "page_content": "Full text string extracted from PDF",
  "metadata": {"source": "CompanyPolicy.pdf", "page": 4}
}
```

**State Object for Graph (TypedDict definition in Python):**
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    intent: str
    requires_human: bool
```

### 3. Workflow Design (LangGraph)

*   **Nodes:**
    *   `router_node(state)`: Analyzes `state["messages"][-1]`. Populates `state["intent"]` and sets `requires_human`.
    *   `retrieve_node(state)`: Connects DB, fetches documents, sets `state["context"]`.
    *   `generate_node(state)`: Runs LLM with `state["context"]` + Prompt template. Injects result into `state["messages"]`.
    *   `human_node(state)`: Pauses. Updates `state["messages"]` with human input.
*   **Edges:**
    *   Start -> `router_node`
    *   Conditional Edge (from `router_node`):
        *   If `require_human == False` -> `retrieve_node`
        *   If `require_human == True` -> `human_node`
    *   `retrieve_node` -> `generate_node`
    *   `generate_node` -> END
    *   `human_node` -> END

### 4. Conditional Routing Logic
A lightweight prompt assesses query intent.
*   **Escalation Criteria Triggered If:**
    *   Query contains heavy frustration ("I am angry", "I demand to speak to someone").
    *   Query requests account deletion, billing disputes, or refund authorization limits overriding typical AI allowance.
    *   **Low confidence / Missing Context:** When the router estimates the standard repository lacks coverage for the request.
*   **Answer Generation Criteria Triggered If:**
    *   General "How to", informational, or policy lookup queries.

### 5. HITL Design
1.  **Escalation Trigger:** The router emits `requires_human=True`.
2.  **State Pause:** LangGraph intercepts the state before reaching `human_node`. An `interrupt` is raised by the graph.
3.  **Action:** The system halts and notifies the terminal operator.
4.  **Human Integration:** Operator types a response. It is wrapped as an `AIMessage(content="[HUMAN AGENT]: " + response)` and appended to the State before continuing to graph END.

### 6. API / Interface Design
Input format (CLI): Raw text string `> User Input: How do I return a damaged product?`
Output format (CLI): `> Support Bot: According to policy, you have 30 days...`
Internal API call formats follow standardized LangChain BaseMessage protocols (`HumanMessage`, `AIMessage`, `SystemMessage`).

### 7. Error Handling
- **Missing Data:** If PDF ingest fails (file not found), abort startup cleanly via `sys.exit`.
- **No Relevant Chunks Found:** If Retriever returns a low distance metric score or empty list, `generate_node` is instructed by its system prompt exactly to reply: "I do not have sufficient information in my knowledge base to answer this." rather than hallucinate.
- **LLM Failure:** Implement retry logic (e.g., `Tenacity` default retries) for connection parsing timeouts to the LLM backend. If it totally fails, return a graceful degradation notice.
