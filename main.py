from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

# Import our RAG system
from contextual_rag import OptimizedContextualRAGSystem

load_dotenv()

llm = init_chat_model(
    "gemini-2.0-flash-001",
     model_provider="google_genai"
)

# Initialize shared RAG system (will load existing data if available)
rag_system = OptimizedContextualRAGSystem(force_rebuild=False)

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional or logical response"
    )

    

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    # Add RAG context to shared state
    rag_context: str | None




def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier = llm.with_structured_output(MessageClassifier)

    result = classifier.invoke([
        {
            "role": "system",
            "content": """classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical' if it asks for facts, information, logical analysis or practical advice
            """
        },
        
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    return {"message_type": result.message_type}



def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}
    
    return {"next": "logical"}


def _get_rag_context(user_message: str) -> str:
    """Helper function to get RAG context if relevant."""
    try:
        # Simple check if the question might benefit from RAG
        question_keywords = ["what", "how", "explain", "tell me", "information", "about"]
        if any(keyword in user_message.lower() for keyword in question_keywords):
            # Query RAG system
            rag_answer = rag_system.query(user_message)
            if rag_answer and "I don't have relevant information" not in rag_answer:
                return f"\n\nRelevant information from knowledge base:\n{rag_answer}"
        return ""
    except Exception as e:
        print(f"RAG query failed: {e}")
        return ""

def therapist_agent(state: State):
    # Trim messages to keep conversation manageable while preserving context
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=2000,
        start_on="human",
        include_system=True,
        allow_partial=False
    )
    
    # Get RAG context for the therapist if relevant
    last_message = state["messages"][-1]
    rag_context = _get_rag_context(last_message.content)
    
    # Build the conversation with system message + RAG context + history
    system_content = """
    You are a compassionate therapist. You provide emotional support, empathy, and helpful guidance for personal problems.
    Use the conversation history to understand the user's situation and respond in a supportive way.
    Be warm, understanding, and focus on the user's emotional well-being.
    Remember previous topics and feelings the user has shared to provide consistent, contextual support.
    """
    
    # Add RAG context if available
    if rag_context:
        system_content += rag_context
    
    conversation_messages = [{"role": "system", "content": system_content}]
    
    # Add the trimmed conversation history
    for msg in trimmed_messages:
        if isinstance(msg, HumanMessage):
            conversation_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            conversation_messages.append({"role": "assistant", "content": msg.content})
    
    reply = llm.invoke(conversation_messages)
    return {"messages": [AIMessage(content=reply.content)], "rag_context": rag_context}




def logical_agent(state: State):
    # Trim messages to keep conversation manageable while preserving context
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=2000,
        start_on="human",
        include_system=True,
        allow_partial=False
    )
    
    # Get RAG context for logical questions
    last_message = state["messages"][-1]
    rag_context = _get_rag_context(last_message.content)
    
    # Build the conversation with system message + RAG context + history
    system_content = """
    You are a logical assistant focused on providing factual information, analysis, and practical solutions.
    Use the conversation history to understand the context and provide well-reasoned, helpful responses.
    Be clear, accurate, and focus on logical problem-solving.
    Reference previous questions and answers when relevant to provide consistent, contextual help.
    """
    
    # Add RAG context if available
    if rag_context:
        system_content += rag_context
    
    conversation_messages = [{"role": "system", "content": system_content}]
    
    # Add the trimmed conversation history
    for msg in trimmed_messages:
        if isinstance(msg, HumanMessage):
            conversation_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            conversation_messages.append({"role": "assistant", "content": msg.content})
    
    reply = llm.invoke(conversation_messages)
    return {"messages": [AIMessage(content=reply.content)], "rag_context": rag_context}




graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    ({"therapist": "therapist", "logical": "logical"}
             ))


graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)


graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None, "rag_context": None}
    
    print("🤖 AI Agent with RAG Integration")
    print("Commands:")
    print("  'exit' - Exit the chatbot")
    print("  'load <filepath>' - Load a document into the knowledge base")
    print("  'stats' - Show RAG system statistics")
    print()
    
    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye...")
            break
        elif user_input.startswith("load "):
            # Handle document loading
            file_path = user_input[5:].strip()
            try:
                chunks_processed = rag_system.load_and_process_documents(file_path)
                print(f"✅ Successfully loaded {chunks_processed} chunks from {file_path}")
            except Exception as e:
                print(f"❌ Failed to load document: {e}")
            continue
        elif user_input == "stats":
            # Show RAG statistics
            try:
                stats = rag_system.get_stats()
                print(f"📊 RAG System Stats:")
                print(f"  Vectorstore exists: {stats['vectorstore_exists']}")
                print(f"  Total chunks: {stats.get('total_chunks', 0)}")
                print(f"  Processed files: {len(stats.get('processed_files', []))}")
            except Exception as e:
                print(f"❌ Failed to get stats: {e}")
            continue
            
        # Use proper LangChain message objects
        user_message = HumanMessage(content=user_input)
        state["messages"] = state.get("messages", []) + [user_message]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            
            # Show if RAG was used
            if state.get("rag_context"):
                print("🔍 [Used knowledge base]")
            
            # Handle both message objects and dictionaries
            if hasattr(last_message, 'content'):
                print(f"Assistant: {last_message.content}")
            elif isinstance(last_message, dict) and 'content' in last_message:
                print(f"Assistant: {last_message['content']}")
            else:
                print(f"Assistant: {last_message}")


if __name__ == "__main__":
    # Check if RAG system is ready
    try:
        stats = rag_system.get_stats()
        if stats['vectorstore_exists']:
            total_chunks = stats.get('total_chunks', 0)
            print(f"✅ RAG system ready with {total_chunks} chunks")
        else:
            print("ℹ️  RAG system initialized but no documents loaded yet")
            print("Use 'load <filepath>' to add documents to the knowledge base")
    except:
        print("⚠️  RAG system initialized")
    
    run_chatbot()

                                      