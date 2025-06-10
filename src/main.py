#!/usr/bin/env python3
"""
Esoteric AI Agent - Main Application

Clean multi-agent system with:
- Emotional and logical response modes
- Domain-aware RAG retrieval
- Q&A cache optimization
- Medium-term memory via summarization
- Clean logging and error handling
"""

from dotenv import load_dotenv
from typing import Annotated, Literal, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
import uuid
import os
import json
from datetime import datetime

from core.contextual_rag import OptimizedContextualRAGSystem
from core.domain_manager import DomainManager
from utils.semantic_domain_detector import SemanticDomainDetector
from cache.negative_intent_detector import NegativeIntentDetector
from cache.qa_cache import QACache
from utils.logger import logger, set_debug_mode
from memory import MemoryManager

load_dotenv()

# Initialize LLM
llm = init_chat_model("gemini-2.0-flash-001", model_provider="google_genai")

# Initialize system components
domain_manager = DomainManager(initial_domains={'lunar', 'ifs'})
semantic_detector = SemanticDomainDetector()
negative_detector = NegativeIntentDetector()
qa_cache = QACache()
rag_system = OptimizedContextualRAGSystem(domain_manager=domain_manager)

# Initialize memory manager with stats collector
memory_manager = MemoryManager(llm, rag_system.stats_collector)

class SessionManager:
    """Simple session management for conversation tracking."""
    
    def __init__(self, sessions_dir: str = "data/sessions"):
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
        
    def create_session(self) -> dict:
        """Create a new session with UUID."""
        session_id = str(uuid.uuid4())
        session_metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "domains_used": [],
            "memory_created": False
        }
        self._save_session_metadata(session_id, session_metadata)
        print(f"🆔 New session created: {session_id[:8]}...")
        return {
            "session_id": session_id,
            "session_metadata": session_metadata
        }
    
    def load_session(self, session_id: str) -> dict:
        """Load an existing session by ID."""
        try:
            session_path = self.get_session_path(session_id)
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    session_metadata = json.load(f)
                print(f"🆔 Loaded session: {session_id[:8]}...")
                return {
                    "session_id": session_id,
                    "session_metadata": session_metadata
                }
            else:
                print(f"❌ Session {session_id[:8]}... not found")
                return None
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        try:
            session_path = self.get_session_path(session_id)
            return os.path.exists(session_path)
        except Exception:
            return False
    
    def find_session_by_partial_id(self, partial_id: str) -> str:
        """Find a session by partial ID (first 8 characters)."""
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json extension
                    if session_id.startswith(partial_id):
                        return session_id
            return None
        except Exception:
            return None
    
    def get_session_path(self, session_id: str) -> str:
        """Get the file path for a session."""
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def _save_session_metadata(self, session_id: str, metadata: dict):
        """Save session metadata to file."""
        try:
            session_path = self.get_session_path(session_id)
            with open(session_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session metadata: {e}")
    
    def update_session_activity(self, session_id: str, domains_used: list = None):
        """Update session activity timestamp and metadata."""
        try:
            session_path = self.get_session_path(session_id)
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata["last_activity"] = datetime.now().isoformat()
                metadata["message_count"] = metadata.get("message_count", 0) + 1
                
                if domains_used:
                    current_domains = set(metadata.get("domains_used", []))
                    current_domains.update(domains_used)
                    metadata["domains_used"] = list(current_domains)
                
                self._save_session_metadata(session_id, metadata)
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
    
    def list_sessions(self, limit: int = 10) -> list:
        """List recent sessions."""
        try:
            session_files = []
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_path = os.path.join(self.sessions_dir, filename)
                    try:
                        with open(session_path, 'r') as f:
                            metadata = json.load(f)
                        session_files.append(metadata)
                    except Exception:
                        continue
            
            # Sort by last activity (newest first)
            session_files.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
            return session_files[:limit]
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

# Initialize session manager
session_manager = SessionManager()

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
    # Medium-term memory fields
    medium_term_summary: str | None
    context: dict[str, Any]  # For tracking summarization state
    # Session tracking
    session_id: str | None
    session_metadata: dict[str, Any] | None

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
    
    # Add memory context to system prompt
    memory_context = memory_manager.build_memory_context(state)
    if memory_context:
        system_content += f"\n\n## Conversation Memory\n{memory_context}\n\nUse this memory context to provide continuity and personalized responses."
    
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
    
    # Get conversation history using centralized memory manager method
    current_message = last_message.content
    conversation_history = memory_manager.get_conversation_history(state, current_message)
    conversation_messages.extend(conversation_history)
    
    reply = llm.invoke(conversation_messages)
    
    # Update memory after response (your "response first, memory later" approach)
    memory_updates = memory_manager.update_medium_term_memory(state)
    
    response_dict = {"messages": [AIMessage(content=reply.content)], "rag_context": rag_context}
    response_dict.update(memory_updates)  # Add any memory updates to the state
    
    return response_dict

def therapist_agent(state: State):
    """Emotional healing and guidance agent."""
    return create_agent_response(state, "emotional")

def logical_agent(state: State):
    """Logical teaching and explanation agent."""
    return create_agent_response(state, "logical")

# Initialize checkpointer for session persistence
checkpointer = MemorySaver()

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

# Compile with checkpointer for session persistence
graph = graph_builder.compile(checkpointer=checkpointer)

def print_stats():
    """Print comprehensive system statistics."""
    try:
        # Use the enhanced stats collector
        rag_system.stats_collector.print_comprehensive_stats(
            vectorstore=rag_system.vectorstore,
            domain_manager=domain_manager,
            qa_cache=qa_cache,
            memory_manager=memory_manager
        )
            
    except Exception as e:
        logger.error(f"Stats error: {e}")

def handle_command(user_input: str, state: dict) -> bool:
    """Handle system commands. Returns True if command was handled."""
    try:
        if user_input == "stats":
            print_stats()
            return True
        elif user_input == "memory":
            # Delegate memory status display to memory manager
            memory_manager.display_memory_status(state)
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
        elif user_input == "memory enable short":
            memory_manager.enable_short_term()
            return True
        elif user_input == "memory disable short":
            memory_manager.disable_short_term()
            return True
        elif user_input == "memory enable medium":
            memory_manager.enable_medium_term()
            return True
        elif user_input == "memory disable medium":
            memory_manager.disable_medium_term()
            return True
        elif user_input == "memory status":
            # Use the same detailed display as "memory" command for consistency
            memory_manager.display_memory_status(state)
            return True
        elif user_input.startswith("session change "):
            session_input = user_input.replace("session change ", "").strip()
            
            if session_input == "new":
                # Create new session and signal to restart
                new_session_info = session_manager.create_session()
                # Store in state to signal restart with new session
                state["_new_session"] = new_session_info
                return "restart_session"
            else:
                # Try to find session by partial ID
                full_session_id = session_manager.find_session_by_partial_id(session_input)
                if full_session_id:
                    session_info = session_manager.load_session(full_session_id)
                    if session_info:
                        # Store in state to signal restart with existing session
                        state["_new_session"] = session_info
                        return "restart_session"
                    else:
                        print(f"❌ Failed to load session {session_input}")
                        return True
                else:
                    print(f"❌ Session not found: {session_input}")
                    print("💡 Use 'session list' to see available sessions")
                    return True
        elif user_input == "session list":
            sessions = session_manager.list_sessions()
            if sessions:
                print("📋 Recent sessions:")
                for i, session in enumerate(sessions[:5]):
                    session_id = session['session_id'][:8]
                    created = session.get('created_at', 'Unknown')[:19].replace('T', ' ')
                    msg_count = session.get('message_count', 0)
                    domains = ', '.join(session.get('domains_used', [])) or 'None'
                    print(f"  {i+1}. {session_id}... ({created}) - {msg_count} msgs, domains: {domains}")
            else:
                print("📋 No sessions found")
            return True
        elif user_input == "session info":
            session_id = state.get("session_id")
            if session_id:
                metadata = state.get("session_metadata", {})
                print(f"🆔 Current Session: {session_id[:8]}...")
                print(f"📅 Created: {metadata.get('created_at', 'Unknown')[:19].replace('T', ' ')}")
                print(f"💬 Messages: {metadata.get('message_count', 0)}")
                print(f"🎯 Domains used: {', '.join(metadata.get('domains_used', [])) or 'None'}")
            else:
                print("🆔 No active session")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return True

def run_chatbot():
    """Main chatbot loop with session management and clean command handling."""
    
    def initialize_session(session_info=None):
        """Initialize or switch to a session."""
        if session_info is None:
            # Create a new session
            session_info = session_manager.create_session()
        
        session_id = session_info["session_id"]
        
        # Initialize state with session info
        state = {
            "messages": [], 
            "message_type": None, 
            "should_use_rag": None, 
            "rag_context": None, 
            "medium_term_summary": None, 
            "context": {},
            "session_id": session_id,
            "session_metadata": session_info["session_metadata"]
        }
        
        # LangGraph configuration for checkpointing
        config = {"configurable": {"thread_id": session_id}}
        
        # Try to restore session state from checkpointer if switching to existing session
        if session_info["session_metadata"].get("message_count", 0) > 0:
            try:
                # Get the current state from checkpointer
                current_state = graph.get_state(config)
                if current_state and current_state.values:
                    print(f"🔄 Restoring conversation with {len(current_state.values.get('messages', []))} messages...")
                    state.update(current_state.values)
                    # Ensure session metadata is preserved
                    state["session_id"] = session_id
                    state["session_metadata"] = session_info["session_metadata"]
                else:
                    print(f"🆔 Switched to session {session_id[:8]}... (empty conversation)")
            except Exception as e:
                print(f"🆔 Switched to session {session_id[:8]}... (new conversation)")
        
        return state, config
    
    # Initialize first session
    current_state, current_config = initialize_session()
    
    # System ready message with active domains (only shown once)
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
    print("Commands: 'exit', 'stats', 'memory', 'domains', 'cache clear', 'debug on/off'")
    print("Memory: 'memory enable/disable short', 'memory enable/disable medium'")
    print("Note: 'memory' and 'memory status' commands show the same detailed information")
    print("Domains: 'domains enable/disable <domain>'")
    print("Sessions: 'session list', 'session info', 'session change <id|new>'")
    print()
    
    while True:
        user_input = input("Message: ")
        
        # Handle exit
        if user_input == "exit":
            print("Bye...")
            break
        
        # Handle commands
        command_result = handle_command(user_input, current_state)
        if command_result == "restart_session":
            # Session change requested
            new_session_info = current_state.get("_new_session")
            if new_session_info:
                current_state, current_config = initialize_session(new_session_info)
                # Remove the temporary session info
                current_state.pop("_new_session", None)
            continue
        elif command_result:
            continue
        
        # Process user message
        try:
            # Add user message to state
            current_state["messages"].append(HumanMessage(content=user_input))
            
            # Process through agent graph with session config
            result = graph.invoke(current_state, config=current_config)
            
            # Update state with result
            current_state.update(result)
            
            # Update session activity
            session_id = current_state["session_id"]
            active_domains = rag_system.get_domain_status().get("active_domains", [])
            session_manager.update_session_activity(session_id, active_domains)
            
            # Update session metadata in state
            if "session_metadata" in current_state:
                current_state["session_metadata"]["message_count"] = current_state["session_metadata"].get("message_count", 0) + 1
                if active_domains:
                    current_domains = set(current_state["session_metadata"].get("domains_used", []))
                    current_domains.update(active_domains)
                    current_state["session_metadata"]["domains_used"] = list(current_domains)
            
            # Display response with cache indicators
            if current_state.get("messages") and len(current_state["messages"]) > 0:
                last_message = current_state["messages"][-1]
                rag_context = current_state.get("rag_context")
                
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
                
                # Add memory indicator if medium-term memory is being used
                if current_state.get("medium_term_summary"):
                    cache_indicator += "🧠 "  # Medium-term memory active
                
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

