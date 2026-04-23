import os
from typing import Annotated, Sequence, TypedDict
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langgraph.graph import StateGraph, START, END

# Define State Type
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    intent: str
    requires_human: bool

class WorkflowOrchestrator:
    def __init__(self, vector_db_path="./chroma_db"):
        # Use Groq API
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load Chroma Vector Store
        print("Connecting to ChromaDB index...")
        self.vectorstore = Chroma(persist_directory=vector_db_path, embedding_function=self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        self.graph = self._build_graph()

    def router_node(self, state: AgentState):
        """Zero-shot LLM routing logic."""
        latest_message = state["messages"][-1].content
        print(f"\n[ROUTER] Analyzing Query: '{latest_message}'")
        
        # We ask LLM to quickly categorize intent
        prompt = f"""Analyze the user's input and classify its intent. 
Input: '{latest_message}'
Is this a standard FAQ/Query, or does it require human escalation? (Escalation = angry, legal threat, extreme frustration, demanding human, or very high value dispute).
Reply EXACTLY with only one of the two following explicit tags: 'STANDARD' or 'ESCALATE'"""
        
        response = self.llm.invoke(prompt)
        intent = response.content.strip().upper()
        
        requires_human = "ESCALATE" in intent
        print(f"[ROUTER] Decision: {intent}")
        return {"intent": intent, "requires_human": requires_human}

    def retrieve_node(self, state: AgentState):
        """RAG Retrieval"""
        latest_message = state["messages"][-1].content
        print("[RETRIEVER] Searching Knowledge Base...")
        docs = self.retriever.invoke(latest_message)
        context = "\n".join([doc.page_content for doc in docs])
        return {"context": context}

    def generate_node(self, state: AgentState):
        """Answer generation given retrieved context."""
        print("[GENERATOR] Synthesizing Answer based on KB...")
        latest_message = state["messages"][-1].content
        context = state.get("context", "")
        
        sys_msg = SystemMessage(content=f"""You are a helpful Acme Corp Customer Support Agent.
Answer the user's question explicitly relying only on the provided context below.
If you don't know the answer or the context is empty, say 'I cannot find the answer in our policy. Would you like me to connect you to an agent?'
Do not hallucinate.

Context:
{context}""")
        
        response = self.llm.invoke([sys_msg, HumanMessage(content=latest_message)])
        return {"messages": [response]}

    def human_node(self, state: AgentState):
        """Dummy human integration node, interrupt execution logic sits in front of this in app.py"""
        # When graph execution arrives here, input has already been provided via app.py interrupt
        print("[HITL] Sending human response down the wire.")
        return {} # Just pass state modifications from external

    def route_condition(self, state: AgentState):
        """Conditional routing mapping."""
        if state["requires_human"]:
            return "escalate"
        return "rag"

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add Nodes
        workflow.add_node("router", self.router_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("human", self.human_node)
        
        # Add Edges
        workflow.add_edge(START, "router")
        
        # Conditional Edge after router
        workflow.add_conditional_edges(
            "router",
            self.route_condition,
            {
                "rag": "retrieve",
                "escalate": "human"
            }
        )
        
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        workflow.add_edge("human", END)
        
        # Compile graph with interruption checkpoint before 'human' node
        from langgraph.checkpoint.memory import MemorySaver
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory, interrupt_before=["human"])
