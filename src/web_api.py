#!/usr/bin/env python3
"""
Esoteric AI Agent - Web API

Simple FastAPI wrapper around the existing CLI agent system.
Provides REST endpoints for chat functionality while preserving all existing features.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import asyncio
from datetime import datetime

# Import existing system components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import (
    rag_system, domain_manager, memory_manager, qa_cache, 
    command_handler, auth_manager, handle_command, print_stats
)

# Import graph and session_manager that are initialized at module level
def get_graph_and_session_manager():
    """Get the initialized graph and session_manager from main module."""
    from src.main import graph, session_manager
    return graph, session_manager
from src.utils.logger import logger
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging for web API
logging.basicConfig(level=logging.INFO)
web_logger = logging.getLogger("esoteric_web_api")

# Initialize FastAPI app
app = FastAPI(
    title="Esoteric AI Agent API",
    description="A wise shaman offering emotional healing and esoteric knowledge through AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for web frontend access
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # Alternative dev port
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Chat request from frontend"""
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response to frontend"""
    response: str
    session_id: str
    message_type: Optional[str] = None  # "emotional" or "logical"
    rag_used: Optional[bool] = None
    cache_hit: Optional[bool] = None
    timestamp: datetime

class SystemStatus(BaseModel):
    """System status information"""
    active_domains: List[str]
    available_domains: List[str]
    total_documents: int
    cache_size: int
    memory_enabled: Dict[str, bool]
    lunar_info: Optional[str] = None

class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    last_activity: datetime
    domains: List[str]

class CommandRequest(BaseModel):
    """System command request"""
    command: str
    session_id: Optional[str] = None

class CommandResponse(BaseModel):
    """System command response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, Dict[str, Any]]:
    """Get existing session or create new one using UnifiedSessionManager"""
    _, session_manager = get_graph_and_session_manager()
    
    if session_id:
        # Try to load existing session
        session_info = session_manager.load_session(session_id)
        if session_info:
            session_manager.current_thread_id = session_id
            return session_id, {
                "state": session_info["state"],
                "config": session_info["config"],
                "created_at": session_info["state"].get("session_metadata", {}).get("created_at"),
                "last_activity": session_info["state"].get("session_metadata", {}).get("last_activity"),
                "message_count": len(session_info["state"].get("messages", []))
            }
    
    # Create new session using existing session manager
    session_info = session_manager.create_session()
    new_session_id = session_info["thread_id"]
    
    return new_session_id, {
        "state": session_info["state"],
        "config": session_info["config"],
        "created_at": session_info["state"].get("session_metadata", {}).get("created_at"),
        "last_activity": session_info["state"].get("session_metadata", {}).get("last_activity"),
        "message_count": len(session_info["state"].get("messages", []))
    }

def update_session_activity(session_id: str):
    """Update session last activity timestamp using UnifiedSessionManager"""
    _, session_manager = get_graph_and_session_manager()
    session_manager.current_thread_id = session_id
    active_domains = rag_system.get_domain_status().get("active_domains", [])
    session_manager.update_activity(active_domains)

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Esoteric AI Agent API",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404s"""
    return {"message": "🌙"}

@app.get("/apple-touch-icon.png")
async def apple_touch_icon():
    """Apple touch icon endpoint to prevent 404s"""
    return {"message": "🌙", "type": "apple-touch-icon"}

@app.get("/apple-touch-icon-precomposed.png")
async def apple_touch_icon_precomposed():
    """Apple touch icon precomposed endpoint to prevent 404s"""
    return {"message": "🌙", "type": "apple-touch-icon-precomposed"}

@app.get("/robots.txt")
async def robots_txt():
    """Robots.txt endpoint"""
    return JSONResponse(
        content="User-agent: *\nDisallow: /\n",
        media_type="text/plain"
    )

@app.get("/manifest.json")
async def manifest_json():
    """Web app manifest for PWA"""
    return {
        "name": "Esoteric AI Agent",
        "short_name": "EsotericAI",
        "description": "A wise shaman offering emotional healing and esoteric knowledge through AI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1a1a1a",
        "theme_color": "#ffd700",
        "icons": [
            {
                "src": "/favicon.ico",
                "sizes": "16x16",
                "type": "application/json"
            }
        ]
    }

@app.get("/chat")
async def chat_info():
    """Information about chat endpoint usage"""
    return {
        "message": "Chat endpoint requires POST method",
        "usage": "POST /chat with JSON body: {'message': 'your message', 'session_id': 'optional'}",
        "example": "curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello!\"}'",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test basic system components
        domain_status = rag_system.get_domain_status()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "rag_system": "operational",
                "domain_manager": "operational", 
                "session_manager": "operational",
                "active_domains": domain_status.get("active_domains", [])
            }
        }
    except Exception as e:
        web_logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - POST only"""
    try:
        # Get or create session
        session_id, session_data = get_or_create_session(request.session_id)
        current_state = session_data["state"]
        current_config = session_data["config"]
        
        web_logger.info(f"Processing message for session {session_id[:8]}...")
        
        # Add user message to state
        current_state["messages"].append(HumanMessage(content=request.message))
        
        # Process through agent graph
        graph, _ = get_graph_and_session_manager()
        result = graph.invoke(current_state, config=current_config)
        
        # Update state with result
        current_state.update(result)
        
        # Update session activity
        update_session_activity(session_id)
        active_domains = rag_system.get_domain_status().get("active_domains", [])
        _, session_manager = get_graph_and_session_manager()
        session_manager.update_activity(active_domains)
        
        # Extract response information
        if current_state.get("messages") and len(current_state["messages"]) > 0:
            last_message = current_state["messages"][-1]
            
            # Determine response type and metadata
            message_type = current_state.get("message_type")
            rag_context = current_state.get("rag_context")
            cache_hit = rag_context == "qa_cache_hit"
            rag_used = bool(rag_context and rag_context != "no_rag")
            
            response_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            return ChatResponse(
                response=response_content,
                session_id=session_id,
                message_type=message_type,
                rag_used=rag_used,
                cache_hit=cache_hit,
                timestamp=datetime.now()
            )
        else:
            raise HTTPException(status_code=500, detail="No response generated")
            
    except Exception as e:
        web_logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status"""
    try:
        domain_status = rag_system.get_domain_status()
        stats = rag_system.get_stats()
        
        # Get lunar information
        lunar_info = None
        try:
            from src.utils.lunar_calculator import get_current_lunar_phase
            lunar_info = get_current_lunar_phase()
        except Exception as e:
            web_logger.debug(f"Could not fetch lunar info: {e}")
        
        return SystemStatus(
            active_domains=domain_status.get("active_domains", []),
            available_domains=domain_status.get("available_domains", []),
            total_documents=stats.get("vectorstore_docs", 0),
            cache_size=qa_cache._get_qa_count() if hasattr(qa_cache, '_get_qa_count') else 0,
            memory_enabled={
                "short_term": True,  # Always enabled
                "medium_term": memory_manager.medium_term_enabled if hasattr(memory_manager, 'medium_term_enabled') else True
            },
            lunar_info=lunar_info
        )
    except Exception as e:
        web_logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving system status")

@app.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions using UnifiedSessionManager"""
    try:
        _, session_manager = get_graph_and_session_manager()
        sessions_list = session_manager.list_sessions(limit=20)
        
        sessions = []
        for session in sessions_list:
            # Parse datetime strings or use current time as fallback
            try:
                created_at = datetime.fromisoformat(session["created_at"]) if session["created_at"] != "unknown" else datetime.now()
                last_activity = datetime.fromisoformat(session["last_activity"]) if session["last_activity"] != "unknown" else datetime.now()
            except:
                created_at = datetime.now()
                last_activity = datetime.now()
            
            sessions.append(SessionInfo(
                session_id=session["thread_id"],
                title=session.get("title"),
                message_count=session["message_count"],
                created_at=created_at,
                last_activity=last_activity,
                domains=session.get("domains_used", [])
            ))
        return sessions
    except Exception as e:
        web_logger.error(f"Session listing error: {e}")
        raise HTTPException(status_code=500, detail="Error listing sessions")

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get chat history for a specific session using UnifiedSessionManager"""
    try:
        _, session_manager = get_graph_and_session_manager()
        session_info = session_manager.load_session(session_id)
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = session_info["state"].get("messages", [])
        
        # Convert messages to API format
        history = []
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                history.append(ChatMessage(
                    role=role,
                    content=msg.content,
                    timestamp=datetime.now()  # Note: we don't store timestamps in current system
                ))
        
        return {"session_id": session_id, "messages": history}
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session history")

@app.put("/sessions/{session_id}/title")
async def update_session_title(session_id: str, request: dict):
    """Update session title"""
    try:
        title = request.get("title", "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        
        _, session_manager = get_graph_and_session_manager()
        
        # Update session title in the database
        success = session_manager.update_session_title(session_id, title)
        
        if success:
            return {"success": True, "message": "Session title updated"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session title update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating session title")

@app.post("/sessions/{session_id}/archive")
async def archive_session(session_id: str):
    """Archive a session"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Archive session in the database
        success = session_manager.archive_session(session_id)
        
        if success:
            return {"success": True, "message": "Session archived"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session archive error: {e}")
        raise HTTPException(status_code=500, detail="Error archiving session")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session permanently"""
    try:
        _, session_manager = get_graph_and_session_manager()
        
        # Delete session from the database
        success = session_manager.delete_session(session_id)
        
        if success:
            return {"success": True, "message": "Session deleted"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        web_logger.error(f"Session deletion error: {e}")
        raise HTTPException(status_code=500, detail="Error deleting session")

@app.post("/command", response_model=CommandResponse)
async def execute_command(request: CommandRequest):
    """Execute system commands"""
    try:
        session_id, session_data = get_or_create_session(request.session_id)
        current_state = session_data["state"]
        
        # Handle command using existing command handler
        result = handle_command(request.command, current_state)
        
        if result == "restart_session":
            # Handle session restart - new session is already created by UnifiedSessionManager
            new_session_info = current_state.get("_new_session")
            if new_session_info:
                new_session_id = new_session_info["thread_id"]
                return CommandResponse(
                    success=True,
                    message="Session changed",
                    data={"new_session_id": new_session_id}
                )
        elif result:
            return CommandResponse(
                success=True,
                message="Command executed successfully"
            )
        else:
            return CommandResponse(
                success=False,
                message="Unknown command or command failed"
            )
            
    except Exception as e:
        web_logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")

@app.get("/domains")
async def get_domains():
    """Get available and active domains"""
    try:
        return rag_system.get_domain_status()
    except Exception as e:
        web_logger.error(f"Domain retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving domains")

@app.post("/domains/{domain_name}/toggle")
async def toggle_domain(domain_name: str, enable: bool = True):
    """Enable or disable a knowledge domain"""
    try:
        if enable:
            result = domain_manager.enable_domain(domain_name)
        else:
            result = domain_manager.disable_domain(domain_name)
        
        if result:
            action = "enabled" if enable else "disabled"
            return {"success": True, "message": f"Domain '{domain_name}' {action}"}
        else:
            return {"success": False, "message": f"Failed to modify domain '{domain_name}'"}
            
    except Exception as e:
        web_logger.error(f"Domain toggle error: {e}")
        raise HTTPException(status_code=500, detail=f"Error toggling domain: {str(e)}")

@app.get("/lunar")
async def get_lunar_info():
    """Get current lunar phase information"""
    try:
        from src.utils.lunar_calculator import get_current_lunar_phase, get_current_lunar_data
        
        summary = get_current_lunar_phase()
        detailed_data = get_current_lunar_data()
        
        return {
            "summary": summary,
            "details": {
                "date": detailed_data.date.isoformat(),
                "phase": detailed_data.phase.value,
                "illumination_percentage": round(detailed_data.illumination_percentage, 1),
                "days_from_new_moon": round(detailed_data.days_from_new_moon, 1),
                "days_to_full_moon": round(detailed_data.days_to_full_moon, 1)
            }
        }
    except Exception as e:
        web_logger.error(f"Lunar info error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving lunar information")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper JSON responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors with proper logging and response"""
    web_logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path),
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🌙 Starting Esoteric AI Agent Web API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Health Check: http://localhost:8000/health")
    print("💬 Chat Endpoint: POST http://localhost:8000/chat")
    
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to prevent double initialization
        log_level="info"
    )