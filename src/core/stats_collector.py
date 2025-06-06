#!/usr/bin/env python3
"""
Statistics Collector for RAG System

Handles collection and reporting of system statistics including:
- Query performance metrics
- Cache statistics  
- Vectorstore information
- Domain configuration
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path


class StatsCollector:
    """
    Collects and manages statistics for the RAG system.
    
    Tracks:
    - Query performance (response times, hit rates)
    - Cache statistics (embedding cache, query cache, precomputed)
    - Vectorstore information
    - Domain configuration
    """
    
    def __init__(self):
        """Initialize statistics collector with default values."""
        self.query_stats = {
            'total_queries': 0,
            'precomputed_hits': 0,
            'cache_hits': 0,
            'rag_processing': 0,
            'domain_blocked': 0,
            'total_time': 0.0,
            'avg_response_time': 0.0
        }
    
    def record_query(self, query_type: str, response_time: float):
        """
        Record a query execution.
        
        Args:
            query_type: Type of query ('precomputed', 'cache', 'rag', 'domain_blocked')
            response_time: Time taken to process the query in seconds
        """
        self.query_stats['total_queries'] += 1
        self.query_stats['total_time'] += response_time
        
        if query_type == 'precomputed':
            self.query_stats['precomputed_hits'] += 1
        elif query_type == 'cache':
            self.query_stats['cache_hits'] += 1
        elif query_type == 'rag':
            self.query_stats['rag_processing'] += 1
        elif query_type == 'domain_blocked':
            self.query_stats['domain_blocked'] += 1
        
        self._update_avg_response_time()
    
    def _update_avg_response_time(self):
        """Update average response time calculation."""
        total_queries = self.query_stats['total_queries']
        if total_queries > 0:
            self.query_stats['avg_response_time'] = self.query_stats['total_time'] / total_queries
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        return self.query_stats.copy()
    
    def get_vectorstore_stats(self, vectorstore) -> Dict[str, Any]:
        """
        Get vectorstore statistics.
        
        Args:
            vectorstore: ChromaDB vectorstore instance
            
        Returns:
            dict: Vectorstore statistics
        """
        stats = {
            'vectorstore_docs': 0,
            'total_chunks': 0
        }
        
        if vectorstore:
            try:
                doc_count = vectorstore._collection.count()
                stats['vectorstore_docs'] = doc_count
                stats['total_chunks'] = doc_count
            except Exception as e:
                stats['vectorstore_error'] = str(e)
        
        return stats
    
    def get_precomputed_stats(self, lunar_cache) -> Dict[str, Any]:
        """
        Get pre-computed response statistics.
        
        Args:
            lunar_cache: Pre-computed response cache instance (or None if disabled)
            
        Returns:
            dict: Pre-computed response statistics
        """
        if lunar_cache is None:
            return {'status': 'disabled', 'message': 'Using unified vector database approach'}
        
        try:
            return lunar_cache.get_stats()
        except Exception as e:
            return {'precomputed_error': str(e)}
    
    def get_query_cache_stats(self, query_cache, enabled: bool) -> Dict[str, Any]:
        """
        Get query similarity cache statistics.
        
        Args:
            query_cache: Query cache instance
            enabled: Whether query cache is enabled
            
        Returns:
            dict: Query cache statistics
        """
        if not enabled or not query_cache:
            return {'enabled': False}
        
        try:
            stats = query_cache.get_cache_summary(return_dict=True)
            stats['enabled'] = True
            return stats
        except Exception as e:
            return {'enabled': False, 'error': str(e)}
    
    def get_embedding_cache_stats(self, persist_directory: str) -> Dict[str, Any]:
        """
        Get embedding cache statistics.
        
        Args:
            persist_directory: Directory where embeddings are cached
            
        Returns:
            dict: Embedding cache statistics
        """
        try:
            embedding_cache_dir = os.path.join(persist_directory, "embedding_cache")
            if os.path.exists(embedding_cache_dir):
                cache_files = list(Path(embedding_cache_dir).glob("*"))
                cache_size = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)  # MB
                return {
                    'cached_embeddings': len(cache_files),
                    'cache_size_mb': round(cache_size, 2),
                    'status': 'active'
                }
            else:
                return {'status': 'not_found'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_comprehensive_stats(self, 
                              domain_manager,
                              vectorstore,
                              lunar_cache,
                              query_cache,
                              query_cache_enabled: bool,
                              persist_directory: str) -> Dict[str, Any]:
        """
        Get comprehensive system statistics.
        
        Args:
            domain_manager: Domain manager instance
            vectorstore: ChromaDB vectorstore instance
            lunar_cache: Pre-computed response cache
            query_cache: Query similarity cache
            query_cache_enabled: Whether query cache is enabled
            persist_directory: Directory for cache storage
            
        Returns:
            dict: Comprehensive system statistics
        """
        stats = {
            'domain_config': domain_manager.get_status(),
            'query_performance': self.get_query_stats(),
        }
        
        # Add vectorstore stats
        stats.update(self.get_vectorstore_stats(vectorstore))
        
        # Add cache statistics
        stats['precomputed_responses'] = self.get_precomputed_stats(lunar_cache)
        stats['query_cache'] = self.get_query_cache_stats(query_cache, query_cache_enabled)
        stats['embedding_cache'] = self.get_embedding_cache_stats(persist_directory)
        
        return stats
    
    def reset_query_stats(self):
        """Reset query performance statistics."""
        self.query_stats = {
            'total_queries': 0,
            'precomputed_hits': 0,
            'cache_hits': 0,
            'rag_processing': 0,
            'domain_blocked': 0,
            'total_time': 0.0,
            'avg_response_time': 0.0
        }
    
    def get_performance_summary(self) -> str:
        """
        Get a formatted performance summary.
        
        Returns:
            str: Formatted performance summary
        """
        stats = self.query_stats
        total = stats['total_queries']
        
        if total == 0:
            return "📊 No queries processed yet"
        
        precomputed_pct = (stats['precomputed_hits'] / total) * 100
        cache_pct = (stats['cache_hits'] / total) * 100
        rag_pct = (stats['rag_processing'] / total) * 100
        blocked_pct = (stats['domain_blocked'] / total) * 100
        
        summary = f"""📊 Query Performance Summary:
  Total queries: {total}
  ⚡ Pre-computed: {stats['precomputed_hits']} ({precomputed_pct:.1f}%)
  🎯 Cache hits: {stats['cache_hits']} ({cache_pct:.1f}%)
  🔍 RAG processing: {stats['rag_processing']} ({rag_pct:.1f}%)
  🚫 Domain blocked: {stats['domain_blocked']} ({blocked_pct:.1f}%)
  ⏱️  Average response time: {stats['avg_response_time']:.3f}s"""
        
        return summary 