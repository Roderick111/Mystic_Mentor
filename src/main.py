#!/usr/bin/env python3
"""
Esoteric AI Agent - Main Application

Clean multi-agent system with:
- Emotional and logical response modes
- Domain-aware RAG retrieval
- Q&A cache optimization
- Clean logging and error handling
"""

from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

from core.contextual_rag import OptimizedContextualRAGSystem
from core.domain_manager import DomainManager
from utils.semantic_domain_detector import SemanticDomainDetector
from cache.negative_intent_detector import NegativeIntentDetector
from cache.qa_cache import QACache
from utils.logger import logger, set_debug_mode

load_dotenv()

# Initialize LLM
llm = init_chat_model("gemini-2.0-flash-001", model_provider="google_genai")

# Initialize system components
domain_manager = DomainManager(initial_domains={'lunar', 'ifs'})
semantic_detector = SemanticDomainDetector()
negative_detector = NegativeIntentDetector()
qa_cache = QACache()
rag_system = OptimizedContextualRAGSystem(domain_manager=domain_manager)

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
- 'logical': discussion of non-personal facts or abstract information, conceptual explanations or analysis, including esoteric topics, knowledge sharing

Use RAG knowledge base if user:
- Shares emotions/moods, asks for psychological support or help
- Asks about esoteric topics: moon phases, astrology, spiritual practices, energy work, numerology, crystals, tarot, etc.
- Asks about therapy or psychological concepts: IFS, Internal Family Systems, parts work, emotional healing, archetypes, shadow work etc.
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
    """Route to appropriate agent based on message type."""
    message_type = state.get("message_type", "logical")
    return {"next": "therapist" if message_type == "emotional" else "logical"}

def get_rag_context(user_message: str, should_use_rag: bool) -> dict:
    """Get RAG context with Q&A cache optimization and clean logging."""
    try:
        if not should_use_rag:
            return {"type": "no_rag", "content": ""}
        
        # Check for negative intent - if detected, skip cache and force RAG
        force_rag = negative_detector.has_negative_intent(user_message)
        
        # Get active domains for filtering
        active_domains = rag_system.get_domain_status().get("active_domains", [])
        
        # Step 1: Q&A Cache Search (unless negative intent detected)
        if not force_rag:
            qa_result = qa_cache.search_qa(user_message, active_domains, k=3)
            if qa_result:
                logger.qa_cache_hit(qa_result['similarity'], user_message[:50])
                return {
                    "type": "qa_cache_hit",
                    "content": qa_result['answer'],
                    "metadata": {
                        "question": qa_result['question'],
                        "domain": qa_result['domain'],
                        "source": qa_result['source'],
                        "similarity": qa_result['similarity'],
                        "qa_id": qa_result['qa_id'],
                        "response_time": qa_result['response_time']
                    }
                }
        
        # Step 2: Regular RAG Search (if Q&A cache missed or negative intent)
        return_type = "negative_intent_bypass" if force_rag else "rag_context"
        
        if force_rag:
            logger.negative_intent(user_message[:50])
        
        # Use RAG system for retrieval with domain filtering
        rag_result = rag_system.query(user_message, k=4)
        
        # Check if we got chunks
        if rag_result and rag_result.get("chunks"):
            chunks_text = "\n\n".join([
                f"[Chunk {chunk['chunk_id']}]: {chunk['content']}"
                for chunk in rag_result["chunks"]
            ])
            return {"type": return_type, "content": chunks_text}
        
        # Check if domain was blocked
        query_type = rag_result.get("metadata", {}).get("query_type", "")
        if query_type == "domain_blocked":
            return {"type": "domain_blocked", "content": rag_result.get("response", "")}
        
        return {"type": "no_rag", "content": ""}
    except Exception as e:
        logger.error(f"RAG Error: {e}")
        return {"type": "no_rag", "content": ""}

def build_domain_guidance(active_domains: list, agent_type: str) -> str:
    """Build domain-specific guidance for agents."""
    if not active_domains:
        return ""
    
    domain_guidance = {
        "emotional": {
            "lunar": "- Consider lunar phases and cosmic timing in your guidance",
            "numerology": "- Incorporate numerological insights when relevant", 
            "ifs": "- Apply Internal Family Systems (IFS) therapy and psychological healing techniques",
            "astrology": "- Reference astrological influences and planetary energies",
            "crystals": "- Suggest crystal healing and energy work when appropriate",
            "tarot": "- Draw upon archetypal wisdom and symbolic insights",
            "archetypes": "- Draw upon Jungian archetypes and symbolic insights"
        },
        "logical": {
            "lunar": "- Explain lunar cycles, moon phases, and cosmic timing with scientific and mystical perspectives",
            "numerology": "- Break down numerological principles and their practical applications",
            "ifs": "- Teach Internal Family Systems (IFS) concepts, parts work, and psychological integration", 
            "astrology": "- Teach astrological concepts with systematic clarity and practical relevance",
            "crystals": "- Explain crystal properties, formations, and energy work methodically",
            "tarot": "- Illuminate tarot symbolism, card meanings, and divination techniques",
            "archetypes": "- Draw upon Jungian archetypes and symbolic insights"
        }
    }
    
    guidance = [domain_guidance[agent_type][domain] for domain in active_domains if domain in domain_guidance[agent_type]]
    
    if guidance:
        header = "Active knowledge domains for enhanced guidance:" if agent_type == "emotional" else "Active knowledge domains for focused teaching:"
        return f"\n\n{header}\n" + "\n".join(guidance)
    
    return ""

def create_agent_response(state: State, agent_type: str) -> dict:
    """Unified agent response creation for both therapist and logical agents."""
    last_message = state["messages"][-1]
    should_use_rag = state.get("should_use_rag", False)
    rag_result = get_rag_context(last_message.content, should_use_rag)
    
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=2000,
        start_on="human",
        include_system=True,
        allow_partial=False
    )
    
    # System prompts for each agent type
    system_prompts = {
        "emotional": """You are a wise shaman offering emotional healing and life guidance. 

Speak from the heart to the heart. Provide warm, intuitive support that honors the user's current emotional state. Draw wisdom from ancient traditions and natural cycles when relevant.

Focus on:
- Deep emotional resonance and validation
- Gentle guidance for self-discovery and healing
- Practical wisdom for personal transformation
- Connection to natural rhythms and inner knowing

Be concise yet profound. Use only the most relevant insights that speak directly to their current experience.""",

        "logical": """You are a wise shaman teacher, illuminating esoteric knowledge with clarity and structure.

Transform complex spiritual concepts into clear, actionable understanding. Your wisdom flows in organized streams - logical, comprehensive, yet deeply intuitive.

Focus on:
- Clear, structured explanations of esoteric concepts
- Practical application of spiritual knowledge
- Connecting ancient wisdom to modern understanding
- Step-by-step guidance for spiritual practices

Be precise yet accessible. Share only the most relevant knowledge that directly serves their current inquiry."""
    }
    
    system_content = system_prompts[agent_type]
    active_domains = rag_system.get_domain_status()["active_domains"]
    system_content += build_domain_guidance(active_domains, agent_type)
    
    rag_context = rag_result["content"]
    rag_type = rag_result["type"]
    
    # Check for domain activation suggestions
    if semantic_detector.is_available():
        try:
            suggestion_result = semantic_detector.get_domain_suggestions(last_message.content, active_domains)
            if suggestion_result["needs_activation"]:
                detected_domain = suggestion_result["detected_domain"]
                domain_display_names = {
                    "lunar": "Lunar Wisdom",
                    "numerology": "Numerology", 
                    "ifs": "Internal Family Systems Therapy",
                    "astrology": "Astrology",
                    "crystals": "Crystal Healing",
                    "tarot": "Tarot & Divination",
                    "archetypes": "Jungian Archetypes"
                }
                domain_display_name = domain_display_names.get(detected_domain, detected_domain.title())
                
                suggestion_message = f"\n\n💡 I notice your question relates to {domain_display_name}. Would you like me to enable this knowledge domain for more detailed guidance? (Type 'domains enable {detected_domain}' to activate)"
                
                # Add suggestion to system content for context
                system_content += f"\n\nNote: The user's question relates to {domain_display_name} domain which is currently inactive. Provide a helpful response with available knowledge and mention the domain activation option."
        except Exception as e:
            logger.debug(f"Domain suggestion error: {e}")
    
    # Handle different types of RAG responses
    if rag_type == "domain_blocked":
        return {"messages": [AIMessage(content=rag_context)], "rag_context": "domain_blocked"}
    elif rag_type == "qa_cache_hit":
        # Direct Q&A cache hit - return the answer directly
        return {"messages": [AIMessage(content=rag_context)], "rag_context": "qa_cache_hit"}
    elif rag_context:
        context_verb = "guidance" if agent_type == "emotional" else "teaching"
        system_content += f"\n\nUse this knowledge to inform your {context_verb}:{rag_context}. Never reference chunk numbers or sources, speak as if the wisdom flows directly from your own understanding."
    
    # Create conversation and get response
    conversation_messages = [{"role": "system", "content": system_content}]
    for msg in trimmed_messages:
        if isinstance(msg, HumanMessage):
            conversation_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            conversation_messages.append({"role": "assistant", "content": msg.content})
    
    reply = llm.invoke(conversation_messages)
    return {"messages": [AIMessage(content=reply.content)], "rag_context": rag_context}

def therapist_agent(state: State):
    """Emotional healing and guidance agent."""
    return create_agent_response(state, "emotional")

def logical_agent(state: State):
    """Logical teaching and explanation agent."""
    return create_agent_response(state, "logical")

# Build the agent graph
graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_and_decide_rag)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges("router", lambda state: state.get("next"), {"therapist": "therapist", "logical": "logical"})
graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()

def print_stats():
    """Print comprehensive system statistics."""
    try:
        # RAG system stats
        stats = rag_system.get_stats()
        total_chunks = stats.get('vectorstore_docs', 0)
        active_domains = len(stats.get('domain_config', {}).get('active_domains', []))
        
        print(f"📊 RAG: {total_chunks} chunks, {active_domains} domains active")
        
        perf = stats.get('query_performance', {})
        if perf.get('total_queries', 0) > 0:
            print(f"⚡ RAG: {perf.get('total_queries', 0)} queries, {perf.get('avg_response_time', 0):.3f}s avg")
        
        # Q&A Cache stats
        qa_stats = qa_cache.get_stats()
        print(f"⚡ Q&A Cache: {qa_stats['total_qa_pairs']} pairs, {qa_stats['hit_rate']:.1f}% hit rate")
        if qa_stats['total_queries'] > 0:
            print(f"📊 Q&A Queries: {qa_stats['total_queries']} total, {qa_stats['avg_response_time']:.3f}s avg")
        
        # System health
        resilience_health = stats.get('resilience_health', {})
        if resilience_health.get('overall_healthy'):
            print("🛡️ System Health: All services operational")
        else:
            print("⚠️ System Health: Some services degraded")
        
        # Domain detection stats
        if semantic_detector.is_available():
            detector_stats = semantic_detector.get_stats()
            print(f"🔍 Domain Detection: {detector_stats['cache_hits']} cache hits, {detector_stats['domains_loaded']} domains loaded")
        else:
            logger.debug("Domain detection not available")
            
    except Exception as e:
        logger.error(f"Stats error: {e}")

def handle_command(user_input: str) -> bool:
    """Handle system commands. Returns True if command was handled."""
    try:
        if user_input == "stats":
            print_stats()
            return True
        elif user_input == "cache clear":
            rag_system.clear_caches()
            return True
        elif user_input == "cache stats clear":
            rag_system.stats_collector.reset_query_stats()
            logger.command_executed("Query statistics cleared")
            return True
        elif user_input == "qa cache clear":
            qa_cache.clear_cache()
            return True
        elif user_input == "domains":
            status = rag_system.get_domain_status()
            active = ', '.join(status['active_domains']) if status['active_domains'] else 'None'
            print(f"🎯 Active: {active}")
            print(f"Available: {', '.join(status['available_domains'])}")
            return True
        elif user_input.startswith("domains enable "):
            domain = user_input.replace("domains enable ", "").strip()
            if rag_system.enable_domain(domain):
                logger.command_executed(f"Domain '{domain}' enabled")
            else:
                logger.error(f"Failed to enable domain '{domain}'")
            return True
        elif user_input.startswith("domains disable "):
            domain = user_input.replace("domains disable ", "").strip()
            if rag_system.disable_domain(domain):
                logger.command_executed(f"Domain '{domain}' disabled")
            else:
                logger.error(f"Failed to disable domain '{domain}'")
            return True
        elif user_input == "debug on":
            set_debug_mode(True)
            return True
        elif user_input == "debug off":
            set_debug_mode(False)
            return True
        
        return False
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return True

def run_chatbot():
    """Main chatbot loop with clean command handling."""
    state = {"messages": [], "message_type": None, "should_use_rag": None, "rag_context": None}
    
    # System ready message with active domains
    stats = rag_system.get_stats()
    total_chunks = stats.get('vectorstore_docs', 0)
    active_domains = stats.get('domain_config', {}).get('active_domains', [])
    
    logger.system_ready(f"Ready with {total_chunks} chunks")
    
    # Show active domains in normal mode
    if active_domains:
        active_domains_str = ', '.join(active_domains)
        print(f"🎯 Active domains: {active_domains_str}")
    else:
        print("🎯 Active domains: None")
    
    print("🤖 Esoteric AI Agent")
    print("Commands: 'exit', 'stats', 'domains', 'cache clear', 'cache stats clear', 'qa cache clear', 'domains enable <domain>', 'domains disable <domain>', 'debug on/off'")
    print()
    
    while True:
        user_input = input("Message: ")
        
        # Handle exit
        if user_input == "exit":
            print("Bye...")
            break
        
        # Handle commands
        if handle_command(user_input):
            continue
        
        # Process user message
        try:
            # Add user message to state
            state["messages"].append(HumanMessage(content=user_input))
            
            # Process through agent graph
            result = graph.invoke(state)
            
            # Update state with result
            state.update(result)
            
            # Display response with cache indicators
            if state.get("messages") and len(state["messages"]) > 0:
                last_message = state["messages"][-1]
                rag_context = state.get("rag_context")
                
                # Response type indicators
                cache_indicator = ""
                if rag_context == "qa_cache_hit":
                    cache_indicator = "⚡ "  # Q&A cache hit
                elif rag_context == "negative_intent_bypass":
                    cache_indicator = "🛡️ "  # Negative intent bypassed cache
                elif rag_context == "domain_blocked":
                    cache_indicator = "🚫 "  # Domain blocked
                elif rag_context:
                    cache_indicator = "🔍 "  # RAG used
                
                if hasattr(last_message, 'content'):
                    print(f"{cache_indicator}Assistant: {last_message.content}")
                elif isinstance(last_message, dict) and 'content' in last_message:
                    print(f"{cache_indicator}Assistant: {last_message['content']}")
                else:
                    print(f"{cache_indicator}Assistant: {last_message}")
            else:
                logger.error("No response generated")
                
        except Exception as e:
            logger.error(f"Processing error: {e}")
            print("I encountered an error processing your message. Please try again.")

if __name__ == "__main__":
    run_chatbot()

