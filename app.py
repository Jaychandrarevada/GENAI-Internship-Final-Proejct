import os
import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from graph_workflow import WorkflowOrchestrator

# Load keys from .env file if it exists
load_dotenv()

# Initialize Graph
if "GROQ_API_KEY" not in os.environ:
    print("WARNING: GROQ_API_KEY environment variable is not set. Groq API will fail.")

orchestrator = None

try:
    if os.path.exists("./chroma_db"):
        orchestrator = WorkflowOrchestrator()
    else:
        print("Warning: ChromaDB not found. Cannot init orchestrator fully.")
except Exception as e:
    print(f"Error initializing orchestrator: {e}")

def chat_function(message, history, session_id):
    if not orchestrator:
        return "System offline. Vector store not initialized or GROQ_API_KEY missing.", session_id
        
    config = {"configurable": {"thread_id": session_id}}
    
    # Check if we are currently waiting on human intervention!
    state = orchestrator.graph.get_state(config)
    if state.next and state.next[0] == "human":
        # The user's message is treated as the Human Agent's response.
        orchestrator.graph.update_state(
            config,
            {"messages": [AIMessage(content=f"[HUMAN AGENT]: {message}")]},
            as_node="human"
        )
        # Continue execution to END
        orchestrator.graph.stream(None, config, stream_mode="values")
        final_state = orchestrator.graph.get_state(config)
        return "(Agent Overrode Response) -> " + final_state.values['messages'][-1].content, session_id
    
    # Standard flow: User query
    events = orchestrator.graph.stream(
        {"messages": [HumanMessage(content=message)]}, 
        config, 
        stream_mode="values"
    )
    
    for _ in events:
        pass
        
    state = orchestrator.graph.get_state(config)
    
    # Check if it halted!
    if state.next and state.next[0] == "human":
        return "⚠️ **SYSTEM HAS ESCALATED TO HUMAN AGENT.** \n*The automated system is paused. Next message entered below will be logged as the Human Agent's intervention response.*", session_id
    
    # Otherwise return normal AI response
    final_state = orchestrator.graph.get_state(config)
    if isinstance(final_state.values["messages"][-1], AIMessage):
         return final_state.values["messages"][-1].content, session_id

    return "Error generating response.", session_id

with gr.Blocks(title="Customer Support Flow") as demo:
    gr.Markdown("# 🤖 RAG Support Dashboard with HITL (Powered by Groq)")
    gr.Markdown("Try typing a standard query like *'What is your return policy?'*. Then try *'I am angry and I want to sue you!'* to trigger human escalation.")
    
    # Local UI State for Session ID
    session_id = gr.State(value="gradio_session_" + str(os.urandom(4).hex()))
    
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(placeholder="Type your message here...", label="User Input")
    clear = gr.ClearButton([msg, chatbot])

    def respond(user_message, chat_history, sess_id):
        bot_message, new_sess_id = chat_function(user_message, chat_history, sess_id)
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history, new_sess_id

    msg.submit(respond, [msg, chatbot, session_id], [msg, chatbot, session_id])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
