#!/usr/bin/env python3
"""
Streamlined RAG System with Direct Chunk Retrieval

Fast document chunk retrieval without intermediate generation,
designed for chatbot systems that handle final response generation.
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional, Set
import chromadb
from chromadb.config import Settings

# LangChain imports
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# IMPORT HANDLING RULE:
# Always keep imports in try-except blocks with proper dummy classes.
# DO NOT remove the try-except structure - it handles missing dependencies gracefully.
# DO ensure all imports are properly structured within the try block.
# DO NOT mix imports inside and outside the try block.

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.domain_manager import DomainManager  
    from core.stats_collector import StatsCollector
except ImportError as e:
    # Dummy classes for graceful degradation
    class DummyDomainManager:
        def __init__(self, active_domains=None): 
            self.active_domains = active_domains or {'lunar'}
        def get_active_domains(self): return self.active_domains
        def get_chroma_filter(self): return {"domain": {"$in": list(self.active_domains)}}
        def enable_domain(self, domain): return True
        def disable_domain(self, domain): return True
        def get_status(self): return {"active_domains": list(self.active_domains)}
        def is_domain_active(self, domain): return domain in self.active_domains
    
    class DummyStatsCollector:
        def record_query(self, query_type, elapsed): pass
        def get_comprehensive_stats(self, **kwargs): return {}
        def get_performance_summary(self): return "Stats not available"
        def reset_query_stats(self): pass
    
    DomainManager = DummyDomainManager
    StatsCollector = DummyStatsCollector

class OptimizedContextualRAGSystem:
    """
    Streamlined RAG system with direct chunk retrieval and multi-domain support.
    
    This system provides fast document chunk retrieval without intermediate generation,
    designed to work with chatbot systems that handle final response generation.
    
    Features:
    - Direct chunk retrieval (no intermediate AI generation)
    - Multi-domain document filtering  
    - Domain-aware query classification
    - Performance monitoring
    """
    
    def __init__(self, 
                 chroma_path: str = "data/chroma_db",
                 collection_name: str = "contextual_rag_collection",
                 domain_manager = None):
        """Initialize the RAG system with domain manager for filtering."""
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.domain_manager = domain_manager
        
        # Initialize stats collector
        self.stats_collector = StatsCollector()
        
        # Initialize embedding model with error handling
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                show_progress_bar=False
            )
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI embeddings: {e}")
            print("⚠️  RAG system will run in limited mode without embeddings")
            self.embeddings = None
        
        # Initialize vector store
        self.vectorstore = None
        self._setup_vectorstore()
        
        if self.domain_manager:
            print(f"✅ RAG System ready - {len(self.domain_manager.get_active_domains())} domains active")
        else:
            print("✅ RAG System ready - no domain filtering")
    
    def _setup_vectorstore(self):
        """Initialize or load the ChromaDB vectorstore."""
        if self.embeddings is None:
            print("⚠️  Cannot initialize vectorstore without embeddings")
            self.vectorstore = None
            return
            
        if os.path.exists(self.chroma_path):
            self.vectorstore = Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            print(f"📚 Vectorstore: {self.vectorstore._collection.count()} documents")
        else:
            self.vectorstore = None
            print("⚠️  No vectorstore found")
    
    def query(self, query_text: str, k: int = 4) -> Dict[str, Any]:
        """
        Enhanced query method with domain filtering at retrieval level.
        
        Args:
            query_text: The user's query
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary containing response, chunks, and metadata
        """
        try:
            start_time = time.time()
            
            # Check if vectorstore is available
            if self.vectorstore is None:
                response_time = time.time() - start_time
                return {
                    "response": "Vector search is not available. Please check embeddings configuration.",
                    "chunks": [],
                    "metadata": {
                        "total_chunks": 0,
                        "response_time": response_time,
                        "query_type": "error"
                    }
                }
            
            # Get active domains for filtering
            active_domains = []
            domain_filter = None
            if self.domain_manager:
                domain_status = self.domain_manager.get_status()
                active_domains = domain_status.get("active_domains", [])
                print(f"🎯 RAG filtering for active domains: {active_domains}")
                
                # Create domain filter for ChromaDB
                domain_filter = {"domain": {"$in": active_domains}}
                print(f"🔍 Applying domain filter: {domain_filter}")
            
            # Retrieve relevant chunks using domain filter
            if domain_filter:
                docs = self.vectorstore.similarity_search(
                    query_text, 
                    k=k,
                    filter=domain_filter
                )
            else:
                docs = self.vectorstore.similarity_search(query_text, k=k)
            
            # Process response
            response_time = time.time() - start_time
            
            if not docs:
                # Handle no documents found
                if domain_filter:
                    print(f"🚫 No content found in active domains: {active_domains}")
                    return {
                        "response": f"I currently don't have information about that topic in my active knowledge areas. My current focus areas are: {', '.join(active_domains)}.",
                        "chunks": [],
                        "metadata": {
                            "total_chunks": 0,
                            "response_time": response_time,
                            "query_type": "domain_blocked"
                        }
                    }
                else:
                    return {
                        "response": "I couldn't find relevant information to answer your question.",
                        "chunks": [],
                        "metadata": {
                            "total_chunks": 0,
                            "response_time": response_time,
                            "query_type": "rag"
                        }
                    }
            
            # Count domains in retrieved docs for stats
            doc_domains = set()
            if self.domain_manager:
                for doc in docs:
                    doc_domain = doc.metadata.get('domain', 'unknown')
                    doc_domains.add(doc_domain)
            
            print(f"📚 Retrieved {len(docs)} chunks from domains: {list(doc_domains)}")
            
            # Record performance stats
            if hasattr(self, 'stats_collector') and self.stats_collector:
                self.stats_collector.record_query('rag', response_time)
            
            # Prepare chunks info
            chunks_info = []
            for i, doc in enumerate(docs):
                chunks_info.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata,
                    "chunk_id": i + 1
                })
            
            return {
                "response": f"Found {len(docs)} relevant chunks for context.",
                "chunks": chunks_info,
                "metadata": {
                    "total_chunks": len(docs),
                    "response_time": response_time,
                    "domains_searched": list(doc_domains) if doc_domains else active_domains,
                    "query_type": "rag"
                }
            }
            
        except Exception as e:
            print(f"❌ RAG query error: {str(e)}")
            return {
                "response": "I encountered an error while searching for information.",
                "chunks": [],
                "metadata": {
                    "total_chunks": 0,
                    "error": str(e),
                    "query_type": "error"
                }
            }
    
    def reload_vectorstore(self):
        """Reload the vectorstore to pick up new documents."""
        self._setup_vectorstore()
        print("✅ Vectorstore reloaded")
    
    def enable_domain(self, domain: str) -> bool:
        """Enable a knowledge domain."""
        return self.domain_manager.enable_domain(domain)
    
    def disable_domain(self, domain: str) -> bool:
        """Disable a knowledge domain."""
        return self.domain_manager.disable_domain(domain)
    
    def get_domain_status(self) -> Dict[str, Any]:
        """Get current domain configuration status."""
        return self.domain_manager.get_status()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return self.stats_collector.get_comprehensive_stats(
            domain_manager=self.domain_manager,
            vectorstore=self.vectorstore,
            lunar_cache=None,  # Disabled - using unified vector database
            query_cache=None,  # Using Q&A cache instead
            query_cache_enabled=False,
            persist_directory=self.chroma_path
        )
    
    def get_performance_summary(self) -> str:
        """Get formatted performance summary."""
        return self.stats_collector.get_performance_summary()
    
    def clear_caches(self):
        """Clear all caching systems."""
        self.stats_collector.reset_query_stats()
        print("✅ Caches cleared")
    
    def __str__(self) -> str:
        """String representation of the RAG system."""
        return f"OptimizedContextualRAGSystem(domains={self.domain_manager.get_active_domains()})"
    
    def __repr__(self) -> str:
        """Detailed representation of the RAG system."""
        return (f"OptimizedContextualRAGSystem("
                f"chroma_path='{self.chroma_path}', "
                f"domains={self.domain_manager.get_active_domains()})") 