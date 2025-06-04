from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain_core.prompts import ChatPromptTemplate

# Import our RAG system
from core.contextual_rag import OptimizedContextualRAGSystem

load_dotenv()

llm = init_chat_model(
    "gemini-2.0-flash-001",
     model_provider="google_genai"
)

# Initialize shared RAG system (will load existing data if available)
rag_system = OptimizedContextualRAGSystem()

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional or logical response"
    )

class CombinedDecision(BaseModel):
    """Combined classification and RAG decision for optimal performance."""
    message_type: Literal["emotional", "logical"] = Field(
        description="Whether message needs emotional or logical response"
    )
    should_use_rag: bool = Field(
        description="True if query involves emotions, spiritual topics, or lunar wisdom"
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    should_use_rag: bool | None
    # Add RAG context to shared state
    rag_context: str | None




def classify_and_decide_rag(state: State):
    """Combined message classification and RAG decision for optimal performance."""
    last_message = state["messages"][-1]
    combined_classifier = llm.with_structured_output(CombinedDecision)

    result = combined_classifier.invoke([
        {
            "role": "system",
            "content": """Classify message type and decide RAG usage:
            
Message types: 
- 'emotional': personal problems or feelings, relationship issues, request for psychological support, therapy or help
- 'logical': discussion of non-personal facts or abstractinformation, conceptual explanations or analysis, including esoteric topics, knowledge sharing

Use RAG knowledge base if user:
- Shares emotions/moods, asks for psychological support or help
- Asks about esoteric topics: moon phases, astrology, spiritual practices, energy work
- Has unexplained emotional states (anxiety, restlessness, disconnection without clear cause)
- Seeks guidance on spiritual timing or lunar influences

Do NOT use RAG for:

- Simple greetings or general conversation  
- Non-esoteric and non-emotional topics (weather, cooking, geography)"""
        },
        
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    
    return {
        "message_type": result.message_type,
        "should_use_rag": result.should_use_rag
    }



def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}
    
    return {"next": "logical"}


def _get_rag_context_optimized(user_message: str, should_use_rag: bool) -> dict:
    """Optimized RAG context retrieval - returns direct response for pre-computed hits."""
    try:
        if not should_use_rag:
            print(f"💭 RAG decision: No (combined classifier)")
            return {"type": "no_rag", "content": ""}
        
        print(f"💭 RAG decision: Yes (combined classifier)")
        
        # Check for pre-computed response first
        from cache.precomputed_lunar_responses import lunar_cache
        precomputed_response = lunar_cache.find_response(user_message)
        if precomputed_response:
            print(f"⚡ PRE-COMPUTED HIT: Direct response")
            return {"type": "direct_response", "content": precomputed_response}
        
        # Query RAG system for similarity cache or full RAG
        rag_answer = rag_system.query(user_message)
        if rag_answer and "I don't have relevant information" not in rag_answer:
            return {"type": "rag_context", "content": f"\n\nRelevant information from knowledge base:\n{rag_answer}"}
        
        return {"type": "no_rag", "content": ""}
    except Exception as e:
        print(f"RAG query failed: {e}")
        return {"type": "no_rag", "content": ""}

def therapist_agent(state: State):
    # Get RAG context for the therapist if relevant
    last_message = state["messages"][-1]
    should_use_rag = state.get("should_use_rag", False)
    rag_result = _get_rag_context_optimized(last_message.content, should_use_rag)
    
    # Handle direct pre-computed responses
    if rag_result["type"] == "direct_response":
        return {"messages": [AIMessage(content=rag_result["content"])], "rag_context": "pre-computed"}
    
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
    
    # Build the conversation with system message + RAG context + history
    system_content = """You are a wise shaman offering emotional healing and life guidance. 

Speak from the heart to the heart. Provide warm, intuitive support that honors the user's current emotional state. Draw wisdom from ancient traditions and natural cycles when relevant.

Focus on:
- Deep emotional resonance and validation
- Gentle guidance for self-discovery and healing
- Practical wisdom for personal transformation
- Connection to natural rhythms and inner knowing

Be concise yet profound. Use only the most relevant insights that speak directly to their current experience."""
    
    # Add RAG context if available
    rag_context = rag_result["content"]
    if rag_context:
        system_content += f"\n\nRelevant esoteric wisdom:{rag_context}"
    
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
    # Get RAG context for logical questions
    last_message = state["messages"][-1]
    should_use_rag = state.get("should_use_rag", False)
    rag_result = _get_rag_context_optimized(last_message.content, should_use_rag)
    
    # Handle direct pre-computed responses
    if rag_result["type"] == "direct_response":
        return {"messages": [AIMessage(content=rag_result["content"])], "rag_context": "pre-computed"}
    
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
    
    # Build the conversation with system message + RAG context + history
    system_content = """You are a wise shaman teacher, illuminating esoteric knowledge with clarity and structure.

Transform complex spiritual concepts into clear, actionable understanding. Your wisdom flows in organized streams - logical, comprehensive, yet deeply intuitive.

Focus on:
- Clear, structured explanations of esoteric concepts
- Practical application of spiritual knowledge
- Connecting ancient wisdom to modern understanding
- Step-by-step guidance for spiritual practices

Be precise yet accessible. Share only the most relevant knowledge that directly serves their current inquiry."""
    
    # Add RAG context if available
    rag_context = rag_result["content"]
    if rag_context:
        system_content += f"\n\nRelevant esoteric knowledge:{rag_context}"
    
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
graph_builder.add_node("classifier", classify_and_decide_rag)
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
    state = {"messages": [], "message_type": None, "should_use_rag": None, "rag_context": None}
    
    print("🤖 AI Agent with RAG + Query Similarity Cache + Pre-computed Responses")
    print("Commands:")
    print("  'exit' - Exit the chatbot")
    print("  'load <filepath>' - Load a document into the knowledge base")
    print("  'stats' - Show comprehensive system statistics")
    print("  'cache clear' - Clear query similarity cache")
    print("  'cache stats' - Show detailed cache performance")
    print("  'precomputed stats' - Show pre-computed response statistics")
    print("  'precomputed clear' - Clear pre-computed hit counts")
    print("  'precomputed list' - List all pre-computed questions by category")
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
            # Show comprehensive RAG statistics
            try:
                stats = rag_system.get_stats()
                print(f"📊 RAG System Statistics:")
                print(f"  Total chunks: {stats.get('total_chunks', 0)}")
                
                # Show query performance stats
                perf_stats = stats.get('query_performance', {})
                if perf_stats:
                    print(f"\n🚀 Query Performance:")
                    print(f"  Total queries: {perf_stats.get('total_queries', 0)}")
                    print(f"  Pre-computed hits: {perf_stats.get('precomputed_hits', 0)}")
                    print(f"  Cache hits: {perf_stats.get('cache_hits', 0)}")
                    print(f"  RAG processing: {perf_stats.get('rag_processing', 0)}")
                    print(f"  Average response time: {perf_stats.get('avg_response_time', 0):.3f}s")
                
                # Show pre-computed response stats
                precomputed_stats = stats.get('precomputed_responses', {})
                if precomputed_stats:
                    print(f"\n⚡ Pre-computed Responses:")
                    print(f"  Total responses: {precomputed_stats.get('total_precomputed_responses', 0)}")
                    print(f"  Total hits: {precomputed_stats.get('total_cache_hits', 0)}")
                    print(f"  Most popular: {precomputed_stats.get('most_popular_question', 'None')} ({precomputed_stats.get('most_popular_hits', 0)} hits)")
                    print(f"  Cache size: {precomputed_stats.get('cache_file_size', '0 MB')}")
                
                # Show embedding cache stats
                cache_stats = stats.get('embedding_cache', {})
                if cache_stats and cache_stats.get('status') != 'error':
                    print(f"\n⚡ Embedding Cache:")
                    print(f"  Cached embeddings: {cache_stats.get('cached_embeddings', 0)}")
                    print(f"  Cache size: {cache_stats.get('cache_size_mb', 0)} MB")
                    print(f"  Status: {cache_stats.get('status', 'unknown')}")
                
                # Show query similarity cache stats
                query_cache_stats = stats.get('query_cache', {})
                if query_cache_stats.get('enabled'):
                    print(f"\n🎯 Query Similarity Cache:")
                    print(f"  Cached queries: {query_cache_stats.get('cached_queries', 0)}")
                    print(f"  Total hits: {query_cache_stats.get('total_hits', 0)}")
                    print(f"  Cache size: {query_cache_stats.get('cache_size_mb', 0)} MB")
                    print(f"  Similarity threshold: {query_cache_stats.get('similarity_threshold', 0.85)}")
                    
                    hit_dist = query_cache_stats.get('hit_distribution', {})
                    if hit_dist:
                        print(f"  Hit distribution: {' | '.join(f'{k}: {v}' for k, v in hit_dist.items())}")
                else:
                    print(f"\n🎯 Query Similarity Cache: Disabled")
                    
            except Exception as e:
                print(f"❌ Failed to get stats: {e}")
            continue
        elif user_input == "cache clear":
            # Clear query similarity cache
            try:
                if hasattr(rag_system, 'query_cache') and rag_system.query_cache:
                    rag_system.query_cache.clear_cache()
                    print("✅ Query similarity cache cleared")
                else:
                    print("ℹ️  Query cache not enabled")
            except Exception as e:
                print(f"❌ Failed to clear cache: {e}")
            continue
        elif user_input == "cache stats":
            # Show detailed cache performance
            try:
                if hasattr(rag_system, 'query_cache') and rag_system.query_cache:
                    summary = rag_system.query_cache.get_cache_summary()
                    print(summary)
                else:
                    print("ℹ️  Query cache not enabled")
            except Exception as e:
                print(f"❌ Failed to get cache stats: {e}")
            continue
        elif user_input == "precomputed stats":
            # Show detailed pre-computed response statistics
            try:
                from cache.precomputed_lunar_responses import lunar_cache
                stats = lunar_cache.get_stats()
                print(f"⚡ PRE-COMPUTED RESPONSE STATISTICS")
                print(f"=" * 40)
                print(f"Total responses available: {stats['total_precomputed_responses']}")
                print(f"Total cache hits: {stats['total_cache_hits']}")
                print(f"Cache file size: {stats['cache_file_size']}")
                print(f"Most popular question: {stats['most_popular_question'] or 'None'}")
                print(f"Most popular hits: {stats['most_popular_hits']}")
                
                print(f"\n📂 Categories:")
                categories = stats['categories']
                for category, count in categories.items():
                    print(f"  {category}: {count} responses")
                
            except Exception as e:
                print(f"❌ Failed to get pre-computed stats: {e}")
            continue
        elif user_input == "precomputed clear":
            # Clear pre-computed hit counts
            try:
                from cache.precomputed_lunar_responses import lunar_cache
                lunar_cache.clear_cache()
                print("✅ Pre-computed hit counts cleared")
            except Exception as e:
                print(f"❌ Failed to clear pre-computed cache: {e}")
            continue
        elif user_input == "precomputed list":
            # List all pre-computed questions by category
            try:
                from cache.precomputed_lunar_responses import lunar_cache
                categories = lunar_cache.list_categories()
                
                print(f"⚡ PRE-COMPUTED LUNAR KNOWLEDGE QUESTIONS")
                print(f"=" * 50)
                
                for category, questions in categories.items():
                    print(f"\n📂 {category.upper().replace('_', ' ')}:")
                    for i, question in enumerate(questions, 1):
                        print(f"   {i}. {question}")
                
                print(f"\n💡 These questions get instant responses (0.001-0.01s)")
                
            except Exception as e:
                print(f"❌ Failed to list pre-computed questions: {e}")
            continue
            
        # Use proper LangChain message objects
        user_message = HumanMessage(content=user_input)
        state["messages"] = state.get("messages", []) + [user_message]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            
            # Show response source indicator
            rag_context = state.get("rag_context")
            if rag_context == "pre-computed":
                print("⚡ [Pre-computed instant response]")
            elif rag_context:
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
        total_chunks = stats.get('total_chunks', 0) or (stats.get('vectorstore_docs', 0) if 'vectorstore_docs' in stats else 0)
        if total_chunks > 0:
            print(f"✅ RAG system ready with {total_chunks} chunks")
        else:
            print("ℹ️  RAG system initialized but no documents loaded yet")
            print("Use 'load <filepath>' to add documents to the knowledge base")
        
        # Show pre-computed responses status
        precomputed_stats = stats.get('precomputed_responses', {})
        if precomputed_stats:
            total_responses = precomputed_stats.get('total_precomputed_responses', 0)
            total_hits = precomputed_stats.get('total_cache_hits', 0)
            print(f"⚡ Pre-computed responses ready: {total_responses} instant answers ({total_hits} hits)")
        
        # Show query cache status
        query_cache_stats = stats.get('query_cache', {})
        if query_cache_stats and query_cache_stats.get('enabled'):
            cached_queries = query_cache_stats.get('cached_queries', 0)
            if cached_queries > 0:
                print(f"🎯 Query cache loaded with {cached_queries} cached queries")
            else:
                print(f"🎯 Query cache ready (empty)")
        else:
            print(f"🎯 Query cache ready (enabled)")
            
    except Exception as e:
        print(f"⚠️  RAG system initialized (status check failed: {e})")
    
    run_chatbot()

                                      