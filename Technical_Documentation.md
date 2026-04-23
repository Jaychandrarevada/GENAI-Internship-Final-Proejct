# Technical Documentation
## RAG-Based Customer Support Assistant (with LangGraph & HITL)

### 1. Introduction
Retrieval-Augmented Generation (RAG) is a technique that grounds Large Language Models in verifiable, external knowledge. Instead of relying purely on statistical weights initialized during training, RAG injects explicit context fetched from a database right before generation. 
This is critically needed for enterprise software; it minimizes hallucinations and anchors AI decisions to rigid policy documents. In this use case, we are resolving standard customer support queries instantly using ingested knowledge, dramatically lowering overhead.

### 2. System Architecture Explanation
The architecture pivots around a central LangGraph workflow runner. Off-cycle, an ingestion pipeline digitizes a PDF policy manual, slices it, runs string inputs through a neural Embedding Model, and stores the indices in localized persist storage (ChromaDB) for dense vector search operations.

When a query lands:
1. It is ingested by our Workflow Graph.
2. A fast zero-shot classifier LLM acts as an `Intent Router`, determining the nature of the prompt.
3. If trivial, an `AI Retrieval Node` triggers embedding nearest-neighbor algorithms mapping the query against our Database. It synthesizes an answer using the retrieved text as strict bounds.
4. If complex/hostile/angry, it bypasses LLM Generation and flows to the `HITL Escalate Node`, forcing the terminal into an interrupt read-state waiting for an actual human.
5. Control resolves back and prints the final output.

### 3. Design Decisions
- **Chunk Size Choice:** 1000 characters with 150 overlap. Provides an excellent balance. Too small (e.g. 100), and semantic meaning is stripped leaving fragmented nouns. Too large (e.g. 5000), and noise is injected pulling the LLM off-target which drastically increases unneeded token consumption.
- **Embedding Strategy:** Usage of pre-trained sentence transformer or LLM provider embedding APIs. Cosine similarity or L2-distance ensures extremely accurate meaning alignments rather than simple DB keywords match (BM25).
- **Prompt Design Logic:** The core generator relies on an explicit system prompt: "You are a customer service assistant. Use ONLY the given retrieved context to answer the user's question. If you don't know the answer, say so exactly. Do not guess."

### 4. Workflow Explanation (LangGraph)
We utilized LangGraph because it offers strict determinism.
- `router_node`: Validates intents.
- `retrieve_node`: DB interfacing wrapper.
- `generate_node`: Final inference call.
- `human_node`: Triggers system interrupt to hook to stdin.
State transitions are defined using immutable types wrapped via `TypedDict`, ensuring data flowing sequentially is typed safely and easily auditable using memory checkpointers.

### 5. Conditional Logic
Intent detection intercepts basic string matching loopholes. If a user states "Can someone help me???", traditional rules-engines break. Because we use an LLM for classification explicitly trained to identify "escalation intent", we bridge unstructured text complexities directly against conditional IF-ELSE edges.

### 6. HITL Implementation
**Role of human intervention:** While LLMs are impressive, there exist domain-specific edge cases (fraud detection, major refunds) explicitly barred from automation.
**Benefits and Limitations:** Guaranteeing human presence acts as a massive failsafe, ensuring AI doesn’t blindly process hazardous actions. However, it requires staffing; creating asynchronous wait queues instead of synchronous immediate processing limits rapid scale in the short-term.

### 7. Challenges & Trade-offs
- **Retrieval accuracy vs speed:** Adding more DB search clusters increases precision but invokes substantial latency for the end user.
- **Chunk size vs context quality:** Overlapping chunks too deeply duplicates context and increases token bills; under-overlapping fractures continuity and sentence fragmentation.
- **Cost vs performance:** Using cutting-edge LLMs (e.g., Gemini-1.5, GPT-4) vs smaller localized models (Llama-3 8B) balances phenomenal zero-shot reasoning at the expense of variable API cloud pricing.

### 8. Testing Strategy
- **Testing Approach:** Conducted module integration tests passing mocked queries to assert the decision paths taken by the Graph execution trace.
- **Sample Queries Passed:** 
  1. *RAG Routing:* "What is your refund policy duration?" -> Directed to RAG.
  2. *HITL Routing:* "Your service is garbage I demand a manager, I am angry!" -> Correctly trapped and escalated.

### 9. Future Enhancements
- **Multi-document support:** Scaling Chroma collections to support specific metadata routing (e.g., filtering PDF documents by tags prior to dense search).
- **Feedback loop:** Adding thumbs up/down integration post-generation to refine the router node via fine-tuning.
- **Deployment:** Packaging the application into a Docker container and hoisting utilizing FastAPI with a React frontend or via enterprise chat integration like Slack API.
