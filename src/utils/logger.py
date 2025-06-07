#!/usr/bin/env python3
"""
Clean Logging System for Esoteric Vectors

Provides structured logging with debug mode support.
Only shows important messages by default, detailed logs in debug mode.
"""

import os
import logging
from typing import Optional
from enum import Enum

class LogLevel(Enum):
    """Log levels for the system"""
    CRITICAL = "critical"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class EsotericLogger:
    """
    Clean logger for the Esoteric Vectors system.
    
    Shows only important messages by default:
    - System ready messages
    - Q&A cache hits
    - RAG system status
    - Commands and errors
    
    Debug mode shows all technical details.
    """
    
    def __init__(self, debug_mode: Optional[bool] = None):
        """
        Initialize logger.
        
        Args:
            debug_mode: Enable debug logging. If None, reads from ESOTERIC_DEBUG env var
        """
        if debug_mode is None:
            debug_mode = os.getenv('ESOTERIC_DEBUG', 'false').lower() in ('true', '1', 'yes')
        
        self.debug_mode = debug_mode
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup Python logging configuration."""
        # Suppress noisy third-party loggers unless in debug mode
        if not self.debug_mode:
            logging.getLogger('httpx').setLevel(logging.WARNING)
            logging.getLogger('chromadb').setLevel(logging.WARNING)
            logging.getLogger('openai').setLevel(logging.WARNING)
            logging.getLogger('src.utils.resilience').setLevel(logging.WARNING)
    
    def system_ready(self, message: str):
        """Log system ready messages (always shown)."""
        print(f"✅ {message}")
    
    def qa_cache_hit(self, similarity: float, query_preview: str):
        """Log Q&A cache hits (always shown)."""
        print(f"⚡ Q&A Cache Hit! Similarity: {similarity:.3f} for: '{query_preview}...'")
    
    def rag_retrieval(self, chunk_count: int, domains: list):
        """Log RAG retrieval results (always shown)."""
        domain_str = f"from domains: {domains}" if domains else "from all domains"
        print(f"📚 Retrieved {chunk_count} chunks {domain_str}")
    
    def command_executed(self, command: str, result: str = ""):
        """Log command execution (always shown)."""
        if result:
            print(f"✅ {command}: {result}")
        else:
            print(f"✅ {command}")
    
    def error(self, message: str):
        """Log errors (always shown)."""
        print(f"❌ {message}")
    
    def warning(self, message: str):
        """Log warnings (always shown)."""
        print(f"⚠️ {message}")
    
    def negative_intent(self, query_preview: str):
        """Log negative intent detection (always shown)."""
        print(f"🛡️ Negative intent detected - bypassing Q&A cache, using RAG for: '{query_preview}...'")
    
    def domain_blocked(self, domains: list):
        """Log domain blocking (always shown)."""
        print(f"🚫 No content found in active domains: {domains}")
    
    def debug(self, message: str):
        """Log debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🔧 DEBUG: {message}")
    
    def debug_resilience(self, message: str):
        """Log resilience debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🛡️ RESILIENCE: {message}")
    
    def debug_chromadb(self, message: str):
        """Log ChromaDB debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🗄️ CHROMADB: {message}")
    
    def debug_openai(self, message: str):
        """Log OpenAI debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🤖 OPENAI: {message}")
    
    def debug_optimization(self, message: str):
        """Log optimization debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🔍 OPTIMIZATION: {message}")
    
    def debug_health(self, message: str):
        """Log health check debug messages (only in debug mode)."""
        if self.debug_mode:
            print(f"🏥 HEALTH: {message}")

# Global logger instance
logger = EsotericLogger()

def set_debug_mode(enabled: bool):
    """Enable or disable debug mode globally."""
    global logger
    logger.debug_mode = enabled
    logger._setup_logging()
    if enabled:
        logger.debug("Debug mode enabled")
    else:
        print("✅ Debug mode disabled")

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return logger.debug_mode 