#!/usr/bin/env python3
"""
Simple Query Similarity Cache Implementation

This cache stores RAG responses and retrieves them for semantically similar queries,
providing significant performance improvements by avoiding repeated processing.

Based on LangChain's semantic caching patterns with cosine similarity.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from langchain_openai import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings


@dataclass
class CachedQuery:
    """Represents a cached query and its response."""
    query: str
    embedding: List[float]
    response: str
    timestamp: float
    hit_count: int = 0


class QuerySimilarityCache:
    """
    Simple Query Similarity Cache for RAG responses.
    
    Uses semantic similarity to find and return cached responses for similar queries,
    significantly improving performance for repeated or similar questions.
    """
    
    def __init__(
        self,
        cache_dir: str = "data/chroma_db/query_cache",
        similarity_threshold: float = 0.85,
        max_cache_size: int = 1000
    ):
        """
        Initialize the Query Similarity Cache.
        
        Args:
            cache_dir: Directory to store cache files
            similarity_threshold: Minimum cosine similarity for cache hits (0.0-1.0)
            max_cache_size: Maximum number of cached queries
        """
        self.cache_directory = Path(cache_dir)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        
        # Cache storage
        self.cache_file = self.cache_directory / "query_cache.json"
        self.queries_cache: Dict[str, CachedQuery] = {}
        
        # Initialize embeddings with caching for performance
        self._setup_embeddings()
        
        # Load existing cache
        self._load_cache()
        
        print(f"🎯 Query Similarity Cache initialized")
        print(f"   Similarity threshold: {similarity_threshold}")
        print(f"   Max cache size: {max_cache_size}")
        print(f"   Loaded {len(self.queries_cache)} cached queries")
    
    def _setup_embeddings(self):
        """Setup cached embeddings for query processing."""
        # Create embedding cache directory
        embedding_cache_dir = self.cache_directory / "embedding_cache"
        embedding_cache_dir.mkdir(exist_ok=True)
        
        # Initialize OpenAI embeddings
        underlying_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Faster and cheaper for query caching
            dimensions=1536  # Smaller dimensions for faster similarity computation
        )
        
        # Create cached embeddings
        embedding_store = LocalFileStore(str(embedding_cache_dir))
        self.embeddings = CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings,
            embedding_store,
            namespace="query_cache_embeddings"
        )
    
    def _load_cache(self):
        """Load existing cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                for query_hash, data in cache_data.items():
                    self.queries_cache[query_hash] = CachedQuery(
                        query=data['query'],
                        embedding=data['embedding'],
                        response=data['response'],
                        timestamp=data['timestamp'],
                        hit_count=data.get('hit_count', 0)
                    )
                    
            except Exception as e:
                print(f"⚠️ Failed to load cache: {e}")
                self.queries_cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            cache_data = {}
            for query_hash, cached_query in self.queries_cache.items():
                cache_data[query_hash] = {
                    'query': cached_query.query,
                    'embedding': cached_query.embedding,
                    'response': cached_query.response,
                    'timestamp': cached_query.timestamp,
                    'hit_count': cached_query.hit_count
                }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    def _get_query_hash(self, query: str) -> str:
        """Generate a hash for the query."""
        return hashlib.md5(query.strip().lower().encode('utf-8')).hexdigest()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Convert to numpy arrays
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return dot_product / (norm_v1 * norm_v2)
            
        except Exception as e:
            print(f"⚠️ Error calculating similarity: {e}")
            return 0.0
    
    def _find_similar_query(self, query_embedding: List[float]) -> Optional[Tuple[str, CachedQuery, float]]:
        """Find the most similar cached query above the threshold."""
        best_match = None
        best_similarity = 0.0
        best_hash = None
        
        for query_hash, cached_query in self.queries_cache.items():
            similarity = self._cosine_similarity(query_embedding, cached_query.embedding)
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = cached_query
                best_hash = query_hash
        
        if best_match:
            return best_hash, best_match, best_similarity
        return None
    
    def _cleanup_cache(self):
        """Remove oldest entries if cache exceeds max size."""
        if len(self.queries_cache) <= self.max_cache_size:
            return
        
        # Sort by timestamp (oldest first) and hit count (least used first)
        sorted_items = sorted(
            self.queries_cache.items(),
            key=lambda x: (x[1].hit_count, x[1].timestamp)
        )
        
        # Remove oldest/least used entries
        entries_to_remove = len(self.queries_cache) - self.max_cache_size + 10  # Remove extra for buffer
        
        for i in range(entries_to_remove):
            if i < len(sorted_items):
                query_hash = sorted_items[i][0]
                del self.queries_cache[query_hash]
        
        print(f"🧹 Cache cleanup: removed {entries_to_remove} old entries")
    
    def get_cached_response(self, query: str) -> Optional[Tuple[str, float]]:
        """
        Get cached response for a query if similar query exists.
        
        Args:
            query: The query to search for
            
        Returns:
            Tuple of (cached_response, similarity_score) if found, None otherwise
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Find similar cached query
            similar_result = self._find_similar_query(query_embedding)
            
            if similar_result:
                query_hash, cached_query, similarity = similar_result
                
                # Update hit count and timestamp
                cached_query.hit_count += 1
                cached_query.timestamp = time.time()  # Update for LRU-like behavior
                
                print(f"🎯 Cache HIT: similarity {similarity:.3f} for query: {query[:50]}...")
                
                return cached_query.response, similarity
            
            print(f"🔍 Cache MISS for query: {query[:50]}...")
            return None
            
        except Exception as e:
            print(f"⚠️ Error getting cached response: {e}")
            return None
    
    def cache_response(self, query: str, response: str):
        """
        Cache a query and its response.
        
        Args:
            query: The original query
            response: The response to cache
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Create cache entry
            query_hash = self._get_query_hash(query)
            cached_query = CachedQuery(
                query=query,
                embedding=query_embedding,
                response=response,
                timestamp=time.time(),
                hit_count=0
            )
            
            # Store in cache
            self.queries_cache[query_hash] = cached_query
            
            # Cleanup if needed
            self._cleanup_cache()
            
            # Save to disk
            self._save_cache()
            
            print(f"💾 Cached response for query: {query[:50]}...")
            
        except Exception as e:
            print(f"⚠️ Error caching response: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.queries_cache:
            return {
                "total_queries": 0,
                "cache_size_mb": 0,
                "hit_distribution": {},
                "average_similarity_threshold": self.similarity_threshold
            }
        
        # Calculate statistics
        total_hits = sum(q.hit_count for q in self.queries_cache.values())
        hit_distribution = {}
        
        for cached_query in self.queries_cache.values():
            hit_range = "0" if cached_query.hit_count == 0 else \
                      "1-5" if cached_query.hit_count <= 5 else \
                      "6-20" if cached_query.hit_count <= 20 else "20+"
            hit_distribution[hit_range] = hit_distribution.get(hit_range, 0) + 1
        
        # Calculate cache file size
        cache_size_mb = 0
        if self.cache_file.exists():
            cache_size_mb = self.cache_file.stat().st_size / (1024 * 1024)
        
        return {
            "total_queries": len(self.queries_cache),
            "total_hits": total_hits,
            "cache_size_mb": round(cache_size_mb, 2),
            "hit_distribution": hit_distribution,
            "similarity_threshold": self.similarity_threshold,
            "max_cache_size": self.max_cache_size
        }
    
    def clear_cache(self):
        """Clear all cached queries."""
        self.queries_cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("🗑️ Query cache cleared")
    
    def get_cache_summary(self) -> str:
        """Get a formatted summary of cache performance."""
        stats = self.get_cache_stats()
        
        if stats["total_queries"] == 0:
            return "📊 Query Similarity Cache: Empty"
        
        return f"""📊 Query Similarity Cache Summary:
  Cached Queries: {stats['total_queries']}
  Total Cache Hits: {stats['total_hits']}
  Cache Size: {stats['cache_size_mb']} MB
  Similarity Threshold: {stats['similarity_threshold']}
  
  Hit Distribution:
    {' | '.join(f"{k}: {v}" for k, v in stats['hit_distribution'].items())}"""


# Convenience function for integration
def create_query_cache(
    cache_dir: str = "data/chroma_db/query_cache",
    similarity_threshold: float = 0.85
) -> QuerySimilarityCache:
    """Create a QuerySimilarityCache instance with default settings."""
    return QuerySimilarityCache(
        cache_dir=cache_dir,
        similarity_threshold=similarity_threshold
    ) 